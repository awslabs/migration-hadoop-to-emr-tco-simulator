from setuptools import setup

setup(
    name="get-aws-product-price",
    version="1.0",
    author="HeejoungSim",
    install_requires=[
        'numpy==1.22.0',
        'boto3==1.18.51',
        'pandas==1.3.5',
        'XlsxWriter==3.0.2',
        'tables==3.7.0',
        'requests==2.27.1'
    ]
)

