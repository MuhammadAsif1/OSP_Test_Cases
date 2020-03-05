#! /bin/bash
list=$(ls -a /home/osp_admin | grep -w .env)
echo "$list"
if [ $list = '.env' ]
then
  echo "=============== Python Environment is Already Created ================"
  version=$(virtualenv --version)
  echo "======== Version of Installed Virtual Environment = $version  =========="
  source /home/osp_admin/r8-14grc
  openstack flavor list
  openstack network list
  openstack server list
else
  echo "============== Creating Virtual Enivironment for Python =============="
  cd /home/osp_admin
  pip install virtualenv
  version=$(virtualenv --version)
  echo "======== Version of Installed Virtual Environment = $version  =========="
  virtualenv -p /usr/bin/python2.7 .env
  export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python2.7
  source .env/bin/activate
fi
