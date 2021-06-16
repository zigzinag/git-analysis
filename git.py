import os
import argparse
import requests
import pandas as pd
import datetime

#python git.py --repository https://github.com/apache/spark --branch branch-3.1

def create_all_url(repository, branch, since, until):
    branch = '?sha=' + branch

    if since is not None:
        since = '&since=' + since + 'T00:00:00Z'
    else: 
        since = ''
    if until is not None:
        until = '&until=' + until + 'T23:59:59Z'
    else: 
        until = ''
    issues = '/issues'
    pulls = '/pulls'
    commits = '/commits'

    url_commits = repository.replace('https://github.com/', 'https://api.github.com/repos/') + commits + branch + since + until + '&per_page=100'
    url_pulls = repository.replace('https://github.com/', 'https://api.github.com/repos/') + pulls + branch + since + until + '&state=all' + '&per_page=100'
    url_issues = repository.replace('https://github.com/', 'https://api.github.com/repos/') + issues + branch + since + until + '&state=all' + '&per_page=100'

    return url_commits, url_pulls, url_issues

def get_commits_data(url):
    commiter = []

    for i in range (15):
        #обусловлено количеством максимальным запросом в час
        url = url + '&page={}'.format(i) 
        repos = requests.get(url)
        if str(repos.json()) == '[]':
            break
        else:
            for i in range(100):
                try:
                    login = repos.json()[i]['committer']['login']
                    commiter.append(login)
                except TypeError:
                    pass
                except IndexError: 
                    break
                except KeyError:
                    print('Ограничение по количеству запросов в час')
                    exit()

    data = {'login': commiter}
    df = pd.DataFrame(data=data)
    df = df.groupby('login').size().reset_index(name='counts').sort_values(by=['counts'], ascending=False).reset_index()
    df = df[(df.index <= 30)].drop(['index'], axis=1)
    
    return df


def pulls_x_issues(url, gap):

    compare_date = datetime.date.today() - datetime.timedelta(gap)

    status_open = 0
    status_close = 0
    old = 0

    repos = requests.get(url)

    for i in range (15):
        #обусловлено количеством максимальным запросом в час
        url = url + '&page={}'.format(i) 
        repos = requests.get(url)
        if str(repos.json()) == '[]':
            break
        else:
            for i in range(100):
                try:
                    status = repos.json()[i]['state']
                    if status == 'open':
                        status_open += 1
                        try:
                            create_date = datetime.datetime.strptime(repos.json()[i]['created_at'], '%Y-%m-%dT%H:%M:%SZ').date()
                            if compare_date > create_date:
                                old += 1
                        except TypeError:
                            pass
                    else:
                        status_close += 1
                except TypeError:
                    pass
                except IndexError: 
                    break
                except KeyError:
                    print('Ограничение по количеству запросов в час')
                    exit()

    data = {'open': [status_open], 'close': [status_close], 'old': [old]}
    df = pd.DataFrame(data=data)

    return df

def print_result(commits_dataframe, pulls_dataframe, issues_dataframe):

    print('Самые активные участники.\n', commits_dataframe)
    print()
    print('Pull requests:\n', pulls_dataframe)
    print()
    print('Issues:\n', issues_dataframe)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--repository',
        action='store',
        type=str,
        required=False
    )
    parser.add_argument(
        '--branch',
        action='store',
        type=str,
        required=False,
        default='master'
    )
    parser.add_argument(
        '--since',
        action='store',
        type=str,
        required=False
    )
    parser.add_argument(
        '--until',
        action='store',
        type=str,
        required=False
    )

    parser = {key: value for key, value in vars(parser.parse_args()).items() if value}

    repository = parser.get('repository')
    branch = parser.get('branch')
    since = parser.get('since')
    until = parser.get('until')

    url_commits, url_pulls, url_issues = create_all_url(repository, branch, since, until)

    commits_dataframe = get_commits_data(url_commits)
    pulls_dataframe = pulls_x_issues(url_pulls, 30)
    issues_dataframe = pulls_x_issues(url_issues, 14)

    print_result(commits_dataframe, pulls_dataframe, issues_dataframe)

if __name__ == "__main__":
   main()