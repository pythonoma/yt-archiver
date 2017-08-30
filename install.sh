echo "=================================";
echo "Updating system...";
eval 'apt-get -y update';

echo "=================================";
echo "Upgrading system...";
echo "-------------------";
eval 'apt-get -y upgrade';

echo "=================================";
echo "Installing pip3 ...";
echo "-------------------";
eval 'apt install '

echo "=================================";
echo "Installing pip, pip3 & unzip ...";
echo "-----------------";
eval 'apt-get -y install unzip python-pip python3-pip';
eval 'pip install -U pip'

echo "=================================";
echo "Installing aria2 ...";
echo "-----------------------------";
eval "apt-get -y install aria2";

echo "=================================";
echo "Installing youtube-dl...";
echo "------------------------";
eval 'curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/bin/youtube-dl';
eval 'chmod a+rx /usr/bin/youtube-dl';
eval 'pip install -U youtube_dl'
eval 'pip3 install -U youtube_dl'

echo "=================================";
echo "Installing internetarchive...";
echo "-----------------------------";
eval 'pip install internetarchive';
eval 'pip3 install internetarchive';
