import requests


def main():
    response = requests.get('https://www.perimeter81.com/zero-trust-network-access')
    print(f'Response time: {response.elapsed.total_seconds()} seconds')


if __name__ == '__main__':
    main()
