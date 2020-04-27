import argparse
import logging

import tableauserverclient as TSC
import yaml

def main():

    with open('env.yaml') as f:
        env = yaml.load(f,Loader=yaml.FullLoader)
    
    parser = argparse.ArgumentParser(
        description='Logs into the server with u/p or PAT')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--site', '-i', required=True, help='online site')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--username', '-u', help='username to sign in with')
    group.add_argument('--token-name', '-t', help='Name of PAT to login with')

    args = parser.parse_args()
    
    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)
    
    if args.username:
        tableau_auth = TSC.TableauAuth(username=args.username,password=env["PASSWORD"],site_id = args.site)
    else:
        tableau_auth = TSC.PersonalAccessTokenAuth(token_name=args.token_name,personal_access_token=env["PAT"],site_id = args.site)
    server = TSC.Server(args.server)


    with server.auth.sign_in(tableau_auth):
        print('Logged in successfully')
        all_datasources, pagination_item = server.datasources.get()
        print("\nThere are {} datasources on site: ".format(
            pagination_item.total_available))
        print([datasource.name for datasource in all_datasources])


if __name__ == '__main__':
    main()
