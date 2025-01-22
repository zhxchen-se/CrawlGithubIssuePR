import requests
import json
import os
from time import sleep
import pandas as pd
import traceback
from tqdm import tqdm

def get_closed_issues_list(repo_owner, repo_name, personal_token):
    file_path = f'./IssueList/{repo_name}_data.xlsx'
    # 检查文件是否存在
    if os.path.exists(file_path):
        print(f'File already exists, skipping fetching closed issues for repo: {repo_name}')
        return
    
    print(f'Fetching closed issues for repo: {repo_name}')
    res_ls = []
    base_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'
    params = {
        'state': 'closed',
        'labels': 'bug',
        'per_page': 20
    }
    headers = {'Authorization': f'token {personal_token}'}
    page = 1
    while True:
        params['page'] = page
        print(f'Page: {page}')
        response = requests.get(url=base_url, params=params, headers=headers)
        sleep(1)
        if response.status_code == 200:
            closed_issues = json.loads(response.text)
            if not closed_issues:
                break
            for issue in closed_issues:
                dic = {
                    'title': issue['title'],
                    'html_url': issue['html_url'],
                    'closed_at': issue['closed_at']
                }
                res_ls.append(dic)
            page += 1
        else:
            print(f'Error: {response.status_code}')
            break
    df = pd.DataFrame(res_ls)
    df.to_excel(file_path, index=False, engine='xlsxwriter')


# 获取帖子最开头的内容
def get_issue_details(issue_html_url, personal_token):
    api_url = issue_html_url
    headers = {'Authorization': f'token {personal_token}'}
    # 获取 issue 详情
    response = requests.get(url=api_url, headers=headers)
    if response.status_code == 200:
        issue_details = json.loads(response.text)
        issue_data = {
            'title': issue_details['title'],
            'body': issue_details['body'],
        }
        return issue_data
    else:
        print(f'Error fetching issue details: {response.status_code}')
        return None

# 获取帖子评论
def get_issue_comments(issue_html_url,personal_token):
    api_url = issue_html_url + '/comments'
    headers = {'Authorization': f'token {personal_token}'}
    page = 1
    comments = []
    while True:
        params = {
            'page': page,
            'per_page': 20
        }
        response = requests.get(url=api_url, headers=headers, params=params)
        if response.status_code == 200:
            comment = json.loads(response.text)
            comments += comment
            if len(comment) < 20:
                return comments
        else:
            print(f'Error: {response.status_code}')
            return comments
        page += 1

# 拼接帖子的内容
def get_post_content(issue_html_url, personal_token):
    issue_html_url = issue_html_url.replace('https://github.com/', 'https://api.github.com/repos/').replace('/pull/', '/issues/')
    print(f"Fetching post from: {issue_html_url}")
    issue_details = get_issue_details(issue_html_url, personal_token)
    if not issue_details:
        return None
    comments = get_issue_comments(issue_html_url, personal_token)
    post_content = issue_details['body']
    for comment in comments:
        post_content += f"\n\n{comment['user']['login']}:\n{comment['body']}"
    return post_content



def update_file_with_post_content(file, personal_token, issue_range):
    print(f"Getting post content for issues in file: {file}")
    df = pd.read_excel(file, engine='openpyxl')
    df['issue_number'] = df['html_url'].apply(lambda url: int(url.split('/')[-1]))
    if 'post_content' not in df.columns:
        df['post_content'] = ''
    # 已经爬过的不再爬取
    df_filtered = df[df['post_content'].isnull() | (df['post_content'] == '')]
    # 之前人工看过的数字范围也不再爬取
    df_filtered = df_filtered[~df_filtered['issue_number'].between(issue_range[0], issue_range[1])]
    
    def fetch_post_content(url,personal_token):
        try:
            return get_post_content(url, personal_token)
        except Exception as e:
            error_message = f"Error fetching content for URL {url}: {str(e)}"
            error_trace = traceback.format_exc()
            print(f"==>> error_message: {error_message}")
            print(f"==>> error_trace: {error_trace}")
            with open('error_log.txt', 'a') as log_file:
                log_file.write(error_message + '\n')
                log_file.write(error_trace + '\n')
            return None
    
    # 每爬取完一行，就保存一次
    for index, row in tqdm(df_filtered.iterrows(),total=len(df_filtered)):
        post_content = fetch_post_content(row['html_url'], personal_token)
        if post_content is not None:
            df.at[index, 'post_content'] = str(post_content)  # 确保 post_content 是字符串类型
        df.to_excel(file, index=False, engine='xlsxwriter')
        sleep(1.5)

    # df['post_content'] = df_filtered['html_url'].apply(lambda url: fetch_post_content(url, personal_token))
    # df.update(df_filtered)

    df.drop(columns=['issue_number'], inplace=True)
    df.to_excel(file, index=False, engine='xlsxwriter')
    
if __name__ == '__main__':
    # repos = {
    # 'MoveIt2': {'repo_owner': 'moveit', 'repo_name': 'moveit2'},
    # 'Navigation2': {'repo_owner': 'ros-navigation', 'repo_name': 'navigation2'},
    # 'MAVROS': {'repo_owner': 'mavlink', 'repo_name': 'mavros'},
    # 'aerostack2': {'repo_owner': 'aerostack2', 'repo_name': 'aerostack2'},
    # 'turtlebot4': {'repo_owner': 'turtlebot', 'repo_name': 'turtlebot4'},
    # 'ros2_control': {'repo_owner': 'ros-controls', 'repo_name': 'ros2_control','issue_range': (-2, -1)}
    # }
    repos = {
        'MoveIt2': {'repo_owner': 'moveit', 'repo_name': 'moveit2','issue_range': (-2, -1)},
        'Navigation2': {'repo_owner': 'ros-navigation', 'repo_name': 'navigation2','issue_range': (-2, -1)},
        'MAVROS': {'repo_owner': 'mavlink', 'repo_name': 'mavros','issue_range': (-2, -1)},
        'aerostack2': {'repo_owner': 'aerostack2', 'repo_name': 'aerostack2','issue_range': (-2, -1)},
        'turtlebot4': {'repo_owner': 'turtlebot', 'repo_name': 'turtlebot4','issue_range': (-2, -1)},
        'ros2_control': {'repo_owner': 'ros-controls', 'repo_name': 'ros2_control','issue_range': (-2, -1)},
        'Universal_Robots_ROS2_Driver': {'repo_owner': 'UniversalRobots', 'repo_name': 'Universal_Robots_ROS2_Driver','issue_range': (-2, -1)},
        'depthai-ros': {'repo_owner': 'luxonis', 'repo_name': 'depthai-ros','issue_range': (-2, -1)},
        'realsense-ros': {'repo_owner': 'IntelRealSense', 'repo_name': 'realsense-ros','issue_range': (-2, -1)}, 
        'ros2_controllers': {'repo_owner': 'ros-controls', 'repo_name': 'ros2_controllers','issue_range': (-2, -1)},
    }
    personal_token = os.getenv('GITHUB_PERSONAL_TOKEN')

    # 批量爬取issue&pr列表，包括标题+URL
    for repo in repos.values():
        get_closed_issues_list(repo['repo_owner'], repo['repo_name'], personal_token)

    # 获取帖子的发帖内容+comments
    for repo in repos.values():
        file = f'./IssueList/{repo["repo_name"]}_data.xlsx'
        update_file_with_post_content(file, personal_token, repo['issue_range'])

