from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument('organization', metavar='organization', type=str,
                    help='Organization in github whose repositories we will look at')
parser.add_argument('secret_key', metavar='secret', type=str,
                    help='Personal github secret key')
args = parser.parse_args()

BASE_URL: str = 'https://api.github.com'
ORGANIZATION: str = args.organization
TOKEN: str = args.secret_key
