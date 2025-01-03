from openai import OpenAI
import pandas as pd
import os
import traceback
from time import sleep

def get_llm_answer(prompt, client):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. You can help me by answering my questions."},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        answer = response.choices[0].message.content
        print(f"==>> answer: {answer}")
        return answer
    except Exception as e:
        error_message = f"Error fetching LLM answer: {str(e)}"
        error_trace = traceback.format_exc()
        print(f"==>> error_message: {error_message}")
        print(f"==>> error_trace: {error_trace}")
        with open('error_log.txt', 'a') as log_file:
            log_file.write(error_message + '\n')
            log_file.write(error_trace + '\n')
        return None


def update_file_with_llm_answers(file, client):
    df = pd.read_excel(file, engine='openpyxl')
    if 'LLM_Answer' not in df.columns:
        df['LLM_Answer'] = ''

    for index, row in df.iterrows():
        if pd.isna(row['LLM_Answer']) or row['LLM_Answer'] == '':
            if pd.isna(row['post_content']) or row['post_content'] == '':
                print(f"Skipping issue with empty post_content: {row['html_url']}")
                continue
            print(f"Currently asking about issue: {row['html_url']}")
            title = row['title']
            post_content = row['post_content']
            # prompt = f"""Title: {title}\n\nPost Content: {post_content}\n\nPlease provide a detailed answer to the above post content."""
            prompt = f"""
            ```
            Title: {title}
            Post Content: {post_content}
            ```"""
            llm_answer = get_llm_answer(prompt, client)
            if llm_answer is not None:
                df.at[index, 'LLM_Answer'] = llm_answer
                df.to_excel(file, index=False, engine='xlsxwriter')
        # sleep(1.5)
    df.to_excel(file, index=False, engine='xlsxwriter')


if __name__ == '__main__':
    repos = {
        'turtlebot4': {'repo_owner': 'turtlebot', 'repo_name': 'turtlebot4'},
        'aerostack2': {'repo_owner': 'aerostack2', 'repo_name': 'aerostack2'},
        'MoveIt2': {'repo_owner': 'moveit', 'repo_name': 'moveit2'},
        'Navigation2': {'repo_owner': 'ros-navigation', 'repo_name': 'navigation2'},
        'MAVROS': {'repo_owner': 'mavlink', 'repo_name': 'mavros'}
    }
    client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'),
                    base_url="https://api.deepseek.com")
    for repo in repos.values():
        file = f'./IssueList/{repo["repo_name"]}_data.xlsx'
        update_file_with_llm_answers(file, client)
