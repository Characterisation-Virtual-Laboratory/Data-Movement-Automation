### TransferScript
A wrapper script for RClone to allow for automated, parallel file transfers.
Designed for easy configuration and reuse via the associated 'config.json' file.

Logs transfers and sends an alert email on errors.

Can be configured with a list of transfers so multiple source and destination pairs can be managed with a single instance if desired.




### Requirements
Python 3.8+<br>
`$ sudo dnf install python38`<br><br>
RClone v1.61.1+<br>
`$ curl -O https://downloads.rclone.org/rclone-current-linux.amd.zip`




### Download Commands
`$ cd ~/Downloads`<br>
`$ git clone https://github.com/Characterisation-Virtual-Laboratory/Data-Movement-Automation`




### Install Commands
`$ cd ~/Downloads/Data-Movement-Automation`<br>
OPTIONAL: Edit "SCRIPT_NAME" inside "INSTALL.sh" to new name.<br>
	Allows installing multiple copies under different names, useful if running multiple copies<br>
	eg: A copy per microscope, or a separate backup script etc.<br>
`$ sudo /bin/bash ./INSTALL.sh`




### Configuration
Edit the following files:<br>
	/usr/local/scripts/<SCRIPT_NAME>/config.json<br>
		This is where most of your transfer settings are defined.<br>
	/usr/local/scripts/<SCRIPT_NAME>/excludes.txt<br>
		Any files / folders you want to exclude from the transfers.<br>
	/etc/systemd/system/<SCRIPT_NAME>.service<br>
		Set "User=<user_to_run_as>" for the script and RClone transfer.<br>
	/etc/systemd/system/<SCRIPT_NAME>.timer<br>
		Set when you want this to run.<br>

Fix ownership:<br>
`$ sudo chown -R <user_to_run_as> /usr/local/scripts/<SCRIPT_NAME>`<br><br>

Add any required endpoints into rclone (not required for local src / dest):<br>
`$ su <user_to_run_as>`<br>
`$ export RCLONE_CONFIG=/usr/local/scripts/<SCRIPT_NAME>/rclone.conf`<br>
`$ rclone config`<br>
	See: https://rclone.org/commands/rclone_config/




### Enable ###
`$ sudo systemctl enable <SCRIPT_NAME>.timer`
