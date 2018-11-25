Publishing test results as PR comment on Github from Travis CI
=================

If you have ever suffered from going through Travis CI logs to get the list of failing tests, this post is made for you.

TLDR:

add the following in `.travis.yml`:

```
after-script:
    curl -s https://raw.githubusercontent.com/monperrus/gmtft/master/give-me-the-failing-tests.py | python
```

The problem
----------

When there are failing tests on Travis, the only way to get them is to:

1. click on the Travis link on Github
2. scroll down to the end of the log
3. search for the failing tests with Ctrl-F

This is not satisfactory:

* this takes a lot of time, too many clicks and scrolling
* the tests are not available if the log file is too big
* in Java, the test list may be impossible to find succinctly if the failures and errors contain too many text output.

Even worse, if one wants to get the failing tests programmatically, one needs to parse the logs, which is super tedious and brittle. This is stupid since all the logs are usually written in a structured way somewhere (in Java, as XML in `target/surefire-reports`).

The solution
------------

The solution is that the Travis job does two more things at the end of the build:

1. parse the structured test results (eg parse `target/surefire-reports/*.xml` in Java)
2. post the list of failing tests as a pull-request comment.

In order to post, the CI configuration must set up a Github user name and a valid Github token. This can be done in two ways in Travis CI: by setting two repository-level environment variables in the Travis settings or by adding the environment variables in `.travis.yml` (see below). By convention, the two environment variables are `GITHUB_AUTH_USER` and `GITHUB_AUTH_TOKEN`.

One this is done, this last thing to do is to add a last step at the end of the build (or an equivalent variation):

```
after-script:
    curl -s curl -s https://raw.githubusercontent.com/monperrus/gmtft/master/give-me-the-failing-tests.py | python 

```

That's it, you get the list of failing tests as PR comment:

<img src="https://user-images.githubusercontent.com/803666/48984194-184ca800-f0f9-11e8-8552-3bd5d42375c5.png"/>

Notes
-------

* Travis does not decrypt environment variables from pull requests coming from external repositories (for [good security reasons](https://docs.travis-ci.com/user/pull-requests/)). Hence, this technique only works when one creates pull-requests as branch on the same repo as the master branch.

* To encrypt the environment variables:

```
travis encrypt GITHUB_AUTH_USER=monperrus --add
travis encrypt GITHUB_AUTH_TOKEN=eab968657466453eab --add
```
