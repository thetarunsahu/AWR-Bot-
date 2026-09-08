"""Install the Python package, ROS resource marker, inventory, and launch file."""

from glob import glob

from setuptools import find_packages, setup


package_name = 'amr_mission_manager'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools', 'PyYAML'],
    zip_safe=True,
    maintainer='Tarun Kumar Sahu',
    maintainer_email='tarunkumarsahu354@gmail.com',
    description='Warehouse SKU inventory lookup and standalone AMR mission target generation.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mission_manager = amr_mission_manager.mission_manager:main',
            'send_demo_task = amr_mission_manager.demo_task:main',
        ],
    },
)
