# MIT Reserve

Automated script to reserve tennis courts at MIT


## Dependencies

- macOS with launchd
- uv (recommended)
- Python 3.13+ (if not using uv)

It's recommended to use [uv](https://docs.astral.sh/uv/) to manage python version and dependencies but not required. 


## Installation

1. Clone this repository:
   ```bash
   $ git clone https://github.com/username/repository-name.git <workspace_name>
   ```

2. Init uv workspace and install dependencies
    ```bash
    $ cd <workspace_name>
    $ uv init && uv sync
    ```

## Script Configuration

1. Create/edit `credentials.json` with your account credentials
   - Update `username` and `password`
   - Update `user_id` (MIT system user id)
   - Update `event_member_token_reserve_court` (additional constant event token MIT uses)

    The `user_id` and `event_member_token_reserve_court` are backend identifiers that are created for each user. They can be found by inspecting the network requests in the browser dev tools when first logging in.

2. Configure preferred reservation times in the `hours` array in `mitreserve.py`
   ```python
   hours = [19, 18, 20]  # = 7pm, 6pm, 8pm (24-hour format)
   ```

## Automation Setup
1. Modify the plist file with local paths. The paths to update are the `PYTHONPATH` environment variable and both program arguments. 
    ```xml
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>
        <string>/Users/reed/workspace/mitreserve/.venv/lib/python3.13/site-packages</string>
    </dict>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/reed/workspace/mitreserve/.venv/bin/python3</string>
        <string>/Users/reed/workspace/mitreserve/mitreserve.py</string>
    </array>
    ```

    If using uv, just update the prefix to where the repo is cloned to: `<update this>/mitreserve/<stays the same>`

2. **(Optional)** Rename the plist file with your username
    ```bash
    $ mv com.reed.mitreserve.plist com.$(whoami).mitreserve.plist
    ```
    And also update Label in the plist file with your username
    ```xml
    <key>Label</key>
    <string>com.[your username].mitreserve</string>
    ```


3. **(Optional)** Modify the plist with when the script should run. The default is to run at midnight every day
    ```xml
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>0</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    ```

    To get mulitple times a day, make it an array. Specific days can also be set here
    ```xml
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Weekday</key>
            <integer>4</integer>
            <key>Hour</key>
            <integer>20</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Weekday</key>
            <integer>6</integer>
            <key>Hour</key>
            <integer>9</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Weekday</key>
            <integer>6</integer>
            <key>Hour</key>
            <integer>10</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
    ```

    Verify any changes made with `plutil`
    ```bash
    $ plutil com.$(whoami).mitreserve.plist
    ```

4. Copy the plist file to the `/Library/LaunchDaemons` directory and update owner and permissions
    ```bash
    $ cp com.$(whoami).mitreserve.plist /Library/LaunchDaemons
    $ sudo chown root:wheel /Library/LaunchDaemons/com.$(whoami).mitreserve.plist
    $ sudo chmod 644 /Library/LaunchDaemons/com.$(whoami).mitreserve.plist
    ```

5. Bootstrap and enable the service
    ```bash
    $ sudo launchctl bootstrap system /Library/LaunchDaemons/com.$(whoami).mitreserve.plist
    $ sudo launchctl enable system/com.$(whoami).mitreserve.plist
    ```

    Optionally verify that the service is setup with launchd

    ```bash
    $ sudo launchctl list | grep mitreserve
    ```

The script should now run automatically at the configured times.

## Testing and Troubleshooting

### Logs

The script outputs logs to:
- **Standard output**: `/tmp/mitreserve.out`
- **Standard error**: `/tmp/mitreserve.err`

These logs are just `stdout` and `stderr` from the python script. 

### Manual Testing
The script can be run directly with uv or python
```bash
$ uv run mitreserve.py
```

It can also be run through launchd on command (without waiting for automation to run)
```bash
$ sudo launchctl kickstart system/com.$(whoami).mitreserve.plist
```

### Making Changes
If any changes are made to the plist after it's bootstrapped, it will need to be re-bootstrapped for the changes to take affect
```bash
$ sudo launchctl bootout system /Library/LaunchDaemons/com.$(whoami).mitreserve.plist
$ sudo launchctl bootstrap system /Library/LaunchDaemons/com.$(whoami).mitreserve.plist
$ sudo launchctl enable system/com.$(whoami).mitreserve.plist
```

Also make sure any changes to the plist are copied to the `/Library/LaunchDaemons/` version as well.

## Notes

- The script will exit after the first successful reservation. This can be changed to reserve multiple hours.