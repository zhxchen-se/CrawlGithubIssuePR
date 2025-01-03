# CrawlGithubIssuePR
 Crawl issues and prs from GitHub and ask LLM with custom prompt.

## Functions Overview
- `get_closed_issues_list`: This function fetches the titles and URLs of all issues and pull requests (PRs).
- `update_file_with_post_content`: This function retrieves the textual content of issues. You can specify a numeric range to filter out issues and PRs within that range, preventing them from being fetched. If no filtering is needed, set the range to (-2, -1) would be ok.
- `update_file_with_llm_answers`: This function organizes the title and content of each post into a custom prompt and queries the Large Language Model (LLM) for answers. The responses are then saved into the same table.

