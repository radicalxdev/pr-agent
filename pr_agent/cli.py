import argparse
import asyncio
import os

from pr_agent.agent.pr_agent import PRAgent, commands
from pr_agent.config_loader import get_settings
from pr_agent.log import setup_logger

log_level = os.environ.get("LOG_LEVEL", "INFO")
setup_logger(log_level)

def set_parser():
    parser = argparse.ArgumentParser(description='AI based pull request analyzer', usage=
    """\
    Usage: cli.py --pr-url=<URL on supported git hosting service> <command> [<args>].
    For example:
    - cli.py --pr_url=... review
    - cli.py --pr_url=... describe
    - cli.py --pr_url=... improve
    - cli.py --pr_url=... ask "write me a poem about this PR"
    - cli.py --pr_url=... reflect
    - cli.py --issue_url=... similar_issue

    Supported commands:
    - review / review_pr - Add a review that includes a summary of the PR and specific suggestions for improvement.

    - ask / ask_question [question] - Ask a question about the PR.

    - describe / describe_pr - Modify the PR title and description based on the PR's contents.

    - improve / improve_code - Suggest improvements to the code in the PR as pull request comments ready to commit.
    Extended mode ('improve --extended') employs several calls, and provides a more thorough feedback

    - reflect - Ask the PR author questions about the PR.

    - update_changelog - Update the changelog based on the PR's contents.

    - add_docs

    - generate_labels


    Configuration:
    To edit any configuration parameter from 'configuration.toml', just add -config_path=<value>.
    For example: 'python cli.py --pr_url=... review --pr_reviewer.extra_instructions="focus on the file: ..."'
    """)
    parser.add_argument('--pr_url', type=str, help='The URL of the PR to review', default=None)
    parser.add_argument('--issue_url', type=str, help='The URL of the Issue to review', default=None)
    parser.add_argument('command', type=str, help='The', choices=commands, default='review')
    parser.add_argument('rest', nargs=argparse.REMAINDER, default=[])
    return parser

async def async_run_command(pr_url, command):
    # Preparing the command
    run_command_str = f"--pr_url={pr_url} {command.lstrip('/')}"
    args = set_parser().parse_args(run_command_str.split())

    # Run the command. Feedback will appear in GitHub PR comments
    return await async_run(args=args)

async def async_run(inargs=None, args=None):
    parser = set_parser()
    if not args:
        args = parser.parse_args(inargs)
    if not args.pr_url and not args.issue_url:
        parser.print_help()
        return

    command = args.command.lower()
    get_settings().set("CONFIG.CLI_MODE", True)
    if args.issue_url:
        result = await PRAgent().handle_request(args.issue_url, [command] + args.rest)
    else:
        result = await PRAgent().handle_request(args.pr_url, [command] + args.rest)
    if not result:
        parser.print_help()
        
    return result

if __name__ == '__main__':
    asyncio.run(async_run())
