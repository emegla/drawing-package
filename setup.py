import setuptools

setuptools.setup(
    name="drawing_package",
    version="0.1.0",
    author="Emma Megla",
    author_email="emegla@uchicago.edu",
    description="Contains fucntions to analyze drawings",
    #url="https://bitbucket.org/EMK_Lab/coding_tutorial/src/master/",
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'extcolors',
        'opencv-python',
        'seaborn'
    ],
)
