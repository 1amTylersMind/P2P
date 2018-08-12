#!/bin/bash
echo "Configuring P2P Networking"
touch whoAmI.txt
curl ifconfig.me >> whoAmI.txt
# Now that we know external IP for node routing
# start the P2P server
python khan.py
# Clean up local IP information when exiting
rm whoAmI.txt
