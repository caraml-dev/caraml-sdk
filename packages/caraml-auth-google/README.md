# CaraML Google Authentication

Utility package containing functions to authenticate users of the Python SDKs of CaraML.

## Installation

As this package currently only contains utility functions, and is not released to the PyPI repository, using helper 
functions contained in this package requires installing/specifying this package as a Git (VCS) dependency:

To install via `pip`:
```shell
pip install git+https://github.com/caraml-dev/caraml-sdk.git@main#egg=caraml-auth-google&subdirectory=packages/caraml-auth-google
```

To specify this in a `requirements.txt` file:
```txt
caraml-auth-google @ git+https://github.com/caraml-dev/caraml-sdk.git@main#egg=caraml-auth-google&subdirectory=packages/caraml-auth-google
```

## Unit Tests

To run the unit tests, run the following command:
```shell
make test
```