#!/usr/bin/python
# post failing tests (if any) to the corresponding pull-request on Github
# author: Martin Monperrus
# url: https://github.com/monperrus/gmtft

import os
import sys
from glob import glob

# dynamic installation of the required packages
# credits: https://blog.ducky.io/python/2013/08/22/calling-pip-programmatically/
import pip
pip.main(['install', '--user', 'lxml', 'PyGithub'])
import site
reload(site)

from lxml import etree
from github import *

def get_failing_tests_java_maven():
    """ 
    Returns the failing tests in target/surefire-reports
    """
    res = []
    if os.path.exists("target/surefire-reports"):
        for test_result in glob("target/surefire-reports/*.xml"):
            content = open(test_result).read().encode("ascii")
            if bytes(b"--") in content: continue
            doc = etree.XML(content)
            for test_case in doc.xpath('//testcase/failure'):
                res.append(test_case.getparent().attrib['classname']+'#'+test_case.getparent().attrib['name'])
            for test_case in doc.xpath('//testcase/error'):
                res.append(test_case.getparent().attrib['classname']+'#'+test_case.getparent().attrib['name'])
    return res

def clean_comments(**args):
    """ Remove all comments of a given user matching a certain keyword on a pull-rquest"""
    gh = Github(args['login'],args['token'])
    repo = gh.get_repo(args['repo_name'], True)
    pr = repo.get_pull(args['pr_id'])
    # get_issue_comments() must be called and not get_comments()
    for comment in pr.get_issue_comments():
        # login is "spoon-bot" by default
        if args['keyword'] in comment.body and comment.user.login == args['login']:
            print("deleted ",comment)
            comment.delete()


def comment_on_pr(file_content, **args):
    """ remove all comments of a given user """
    gh = Github(args['login'],args['token'])
    repo = gh.get_repo(args['repo_name'], True)
    pr = repo.get_pull(args['pr_id'])
    pr.create_issue_comment(file_content)

failing_tests = get_failing_tests_java_maven()
failed_tests_in_markdown = "\n".join(["* " + x for x in failing_tests])

# in any case, we print the clean list of tests at the end of the log (easier to find than the standard surefire logs
print("detected failing tests: \n"+failed_tests_in_markdown)

# # we only post for the failing tests for pull-requests
# doc: https://docs.travis-ci.com/user/environment-variables/
if 'TRAVIS_PULL_REQUEST' in os.environ and os.environ['TRAVIS_PULL_REQUEST'] != "false":
    
    # we need a github login and token to post on a PR
    if not 'GITHUB_AUTH_USER' in os.environ or not 'GITHUB_AUTH_TOKEN' in os.environ :
        print('gmtft: we need a github login and token to post on a PR')
        sys.exit(0)

    # we comment on the pr
    powered_by = 'Auto-comment by [https://github.com/monperrus/gmtft](gmtft)'
    clean_comments(keyword=powered_by, login = os.environ['GITHUB_AUTH_USER'], token = os.environ['GITHUB_AUTH_TOKEN'], repo_name = os.environ['TRAVIS_REPO_SLUG'], pr_id = int(os.environ['TRAVIS_PULL_REQUEST']))
    msg = "All tests pass, congrats :+1:  \n"+powered_by
    if len(failing_tests) > 0:
        msg = "Failing tests:\n\n"+failed_tests_in_markdown + "\n\n"+powered_by
    comment_on_pr(msg, login = os.environ['GITHUB_AUTH_USER'], token = os.environ['GITHUB_AUTH_TOKEN'], repo_name = os.environ['TRAVIS_REPO_SLUG'], pr_id = int(os.environ['TRAVIS_PULL_REQUEST']))
    print('commented on https://github.com/'+os.environ['TRAVIS_REPO_SLUG']+"/pull/"+os.environ['TRAVIS_PULL_REQUEST'])
else:
    print("no TRAVIS_PULL_REQUEST environment variable, not in a pull request?")

