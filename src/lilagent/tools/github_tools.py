"""GitHub integration tools for agent use."""

from typing import Optional, List, Dict, Any
from github import Github, GithubException
from crewai_tools import BaseTool
from pydantic import BaseModel, Field


class GetIssueInput(BaseModel):
    """Input schema for GetIssueTool."""

    issue_number: int = Field(..., description="Issue number to retrieve")


class GetIssueTool(BaseTool):
    """Tool for getting GitHub issue details."""

    name: str = "get_issue"
    description: str = (
        "Get details of a GitHub issue including title, body, and comments. "
        "Provide the issue number."
    )
    args_schema: type[BaseModel] = GetIssueInput
    github_client: Github = Field(..., description="GitHub API client")
    repo_name: str = Field(..., description="Repository name (owner/repo)")

    def _run(self, issue_number: int) -> str:
        """Get issue details."""
        try:
            repo = self.github_client.get_repo(self.repo_name)
            issue = repo.get_issue(number=issue_number)

            output = []
            output.append(f"Issue #{issue.number}: {issue.title}")
            output.append(f"State: {issue.state}")
            output.append(f"Author: {issue.user.login}")
            output.append(f"Created: {issue.created_at}")
            output.append(f"\n=== DESCRIPTION ===\n{issue.body}")

            comments = list(issue.get_comments())
            if comments:
                output.append(f"\n=== COMMENTS ({len(comments)}) ===")
                for i, comment in enumerate(comments, 1):
                    output.append(
                        f"\n[{i}] {comment.user.login} at {comment.created_at}:\n{comment.body}"
                    )

            return "\n".join(output)

        except GithubException as e:
            return f"Error getting issue: {e.status} - {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error: {str(e)}"


class CommentOnIssueInput(BaseModel):
    """Input schema for CommentOnIssueTool."""

    issue_number: int = Field(..., description="Issue number to comment on")
    comment: str = Field(..., description="Comment text (markdown supported)")


class CommentOnIssueTool(BaseTool):
    """Tool for commenting on GitHub issues."""

    name: str = "comment_on_issue"
    description: str = (
        "Add a comment to a GitHub issue. Use this to ask questions or provide updates. "
        "Supports markdown formatting."
    )
    args_schema: type[BaseModel] = CommentOnIssueInput
    github_client: Github = Field(..., description="GitHub API client")
    repo_name: str = Field(..., description="Repository name (owner/repo)")

    def _run(self, issue_number: int, comment: str) -> str:
        """Comment on issue."""
        try:
            repo = self.github_client.get_repo(self.repo_name)
            issue = repo.get_issue(number=issue_number)
            issue.create_comment(comment)

            return f"✓ Comment added to issue #{issue_number}"

        except GithubException as e:
            return f"Error commenting: {e.status} - {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error: {str(e)}"


class CreatePullRequestInput(BaseModel):
    """Input schema for CreatePullRequestTool."""

    title: str = Field(..., description="PR title")
    body: str = Field(..., description="PR description (markdown supported)")
    head_branch: str = Field(..., description="Branch with changes (e.g., 'feature/new-code')")
    base_branch: str = Field(default="main", description="Target branch (default: main)")


class CreatePullRequestTool(BaseTool):
    """Tool for creating GitHub pull requests."""

    name: str = "create_pull_request"
    description: str = (
        "Create a GitHub pull request from a branch. "
        "Requires code to already be pushed to the head branch. "
        "Returns PR number and URL."
    )
    args_schema: type[BaseModel] = CreatePullRequestInput
    github_client: Github = Field(..., description="GitHub API client")
    repo_name: str = Field(..., description="Repository name (owner/repo)")

    def _run(
        self, title: str, body: str, head_branch: str, base_branch: str = "main"
    ) -> str:
        """Create pull request."""
        try:
            repo = self.github_client.get_repo(self.repo_name)
            pr = repo.create_pull(title=title, body=body, head=head_branch, base=base_branch)

            return (
                f"✓ Pull Request created successfully\n"
                f"PR #{pr.number}: {pr.title}\n"
                f"URL: {pr.html_url}\n"
                f"Branch: {head_branch} → {base_branch}"
            )

        except GithubException as e:
            return f"Error creating PR: {e.status} - {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error: {str(e)}"


class GetPullRequestInput(BaseModel):
    """Input schema for GetPullRequestTool."""

    pr_number: int = Field(..., description="Pull request number")


class GetPullRequestTool(BaseTool):
    """Tool for getting PR details and comments."""

    name: str = "get_pull_request"
    description: str = (
        "Get details of a pull request including status, comments, and review feedback. "
        "Use this to check for user responses or CI status."
    )
    args_schema: type[BaseModel] = GetPullRequestInput
    github_client: Github = Field(..., description="GitHub API client")
    repo_name: str = Field(..., description="Repository name (owner/repo)")

    def _run(self, pr_number: int) -> str:
        """Get PR details."""
        try:
            repo = self.github_client.get_repo(self.repo_name)
            pr = repo.get_pull(number=pr_number)

            output = []
            output.append(f"PR #{pr.number}: {pr.title}")
            output.append(f"State: {pr.state} | Merged: {pr.merged}")
            output.append(f"Author: {pr.user.login}")
            output.append(f"Branch: {pr.head.ref} → {pr.base.ref}")
            output.append(f"Mergeable: {pr.mergeable}")

            # CI status
            if pr.head.sha:
                commit = repo.get_commit(pr.head.sha)
                status = commit.get_combined_status()
                output.append(f"\n=== CI STATUS ===")
                output.append(f"Overall: {status.state}")
                for check in status.statuses:
                    output.append(f"  - {check.context}: {check.state} ({check.description})")

            # Comments
            comments = list(pr.get_issue_comments())
            if comments:
                output.append(f"\n=== COMMENTS ({len(comments)}) ===")
                for i, comment in enumerate(comments, 1):
                    output.append(
                        f"\n[{i}] {comment.user.login} at {comment.created_at}:\n{comment.body}"
                    )

            # Reviews
            reviews = list(pr.get_reviews())
            if reviews:
                output.append(f"\n=== REVIEWS ({len(reviews)}) ===")
                for i, review in enumerate(reviews, 1):
                    output.append(
                        f"\n[{i}] {review.user.login}: {review.state}\n{review.body or '(no comment)'}"
                    )

            return "\n".join(output)

        except GithubException as e:
            return f"Error getting PR: {e.status} - {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error: {str(e)}"


class CommentOnPRInput(BaseModel):
    """Input schema for CommentOnPRTool."""

    pr_number: int = Field(..., description="Pull request number")
    comment: str = Field(..., description="Comment text (markdown supported)")


class CommentOnPRTool(BaseTool):
    """Tool for commenting on pull requests."""

    name: str = "comment_on_pr"
    description: str = (
        "Add a comment to a pull request. Use this to respond to user feedback, "
        "ask questions, or provide updates. Supports markdown formatting."
    )
    args_schema: type[BaseModel] = CommentOnPRInput
    github_client: Github = Field(..., description="GitHub API client")
    repo_name: str = Field(..., description="Repository name (owner/repo)")

    def _run(self, pr_number: int, comment: str) -> str:
        """Comment on PR."""
        try:
            repo = self.github_client.get_repo(self.repo_name)
            pr = repo.get_pull(number=pr_number)
            pr.create_issue_comment(comment)

            return f"✓ Comment added to PR #{pr_number}"

        except GithubException as e:
            return f"Error commenting: {e.status} - {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error: {str(e)}"


class PushToGitHubInput(BaseModel):
    """Input schema for PushToGitHubTool."""

    branch_name: str = Field(..., description="Branch name to push to")
    commit_message: str = Field(..., description="Commit message")


class PushToGitHubTool(BaseTool):
    """Tool for committing and pushing code to GitHub."""

    name: str = "push_to_github"
    description: str = (
        "Commit all changes in the work directory and push to GitHub branch. "
        "Creates branch if it doesn't exist. Use after code generation is complete."
    )
    args_schema: type[BaseModel] = PushToGitHubInput
    work_dir: str = Field(..., description="Work directory with git repository")

    def _run(self, branch_name: str, commit_message: str) -> str:
        """Commit and push to GitHub."""
        try:
            from git import Repo

            repo = Repo(self.work_dir)

            # Create/checkout branch
            try:
                repo.git.checkout('-b', branch_name)
            except:
                repo.git.checkout(branch_name)

            # Add all changes
            repo.git.add(A=True)

            # Commit
            if repo.is_dirty() or repo.untracked_files:
                repo.index.commit(commit_message)
                # Push
                origin = repo.remote('origin')
                origin.push(branch_name)

                return f"✓ Committed and pushed to branch '{branch_name}'"
            else:
                return "No changes to commit"

        except Exception as e:
            return f"Error pushing to GitHub: {str(e)}"


def create_github_tools(
    github_token: str,
    repo_name: str,
    work_dir: Optional[str] = None
) -> List[BaseTool]:
    """Create GitHub tools for agent use.

    Args:
        github_token: GitHub personal access token
        repo_name: Repository name in format 'owner/repo'
        work_dir: Optional work directory for git operations

    Returns:
        List of configured GitHub tools
    """
    github_client = Github(github_token)

    tools = [
        GetIssueTool(github_client=github_client, repo_name=repo_name),
        CommentOnIssueTool(github_client=github_client, repo_name=repo_name),
        GetPullRequestTool(github_client=github_client, repo_name=repo_name),
        CommentOnPRTool(github_client=github_client, repo_name=repo_name),
        CreatePullRequestTool(github_client=github_client, repo_name=repo_name),
    ]

    if work_dir:
        tools.append(PushToGitHubTool(work_dir=work_dir))

    return tools
