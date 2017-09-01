echo "=================================";
echo "Installing pip, pip3 & unzip ...";
echo "-----------------";
eval 'apt-get -y install unzip python-pip python3-pip';
eval 'pip install --upgrade pip'

echo "=================================";
echo "Installing aria2 ...";
echo "-----------------------------";
eval "apt-get -y install aria2";
# fix error 22 https://github.com/aria2/aria2/issues/502
eval "mkdir -p ~/.aria2";
eval "echo 'async-dns=false' >> ~/.aria2/aria2.conf";

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

echo "=================================";
echo "Installing yt-archiver...";
echo "-----------------------------";
eval 'curl -L https://raw.githubusercontent.com/pythonoma/yt-archiver/master/yt_archiver/yt_archiver.py -o /usr/bin/yt-archiver';
eval 'chmod a+rx /usr/bin/yt-archiver';
