import setuptools

setuptools.setup(
    name='loadTradegatePipeline',
    version='0.1',
    install_requires=[
        'sqlalchemy'
    ],
    packages={'gcp':'gcp'}
    #setuptools.find_namespace_packages()
)
