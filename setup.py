

from setuptools import setup, find_packages

setup(
    name='nonebot_plugin_pixiv',
    version="1.0.7",
    description=(
        'pixiv.net 查询图片，支持动图和多图'
    ),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='anlen123',
    author_email='1761512493@qq.com',
    maintainer='anlen123',
    maintainer_email='1761512493@qq.com',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/anlen123/nonebot_plugin_pixiv',
    install_requires=[
        'aiohttp',
        'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
        'nonebot2>=2.0.0-beta.1,<3.0.0',
        'opencv-python'
    ]
)
