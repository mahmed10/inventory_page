from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import csv
import os
import yaml

app = Flask(__name__)

# Path to the CSV file
csv_file = "lab_inventory.csv"
request_file = 'request_inventory.csv'

with open("user_info.yaml", 'r') as stream:
    user_info = yaml.safe_load(stream)

# Dummy user data (replace with a proper authentication mechanism)
# users = {
#     "user1": "a",
#     "user2": "2",
#     "user3": ""
# }
users = user_info['user']
admin_users = user_info['admin']
# Extracting user names from the user_info dictionary
user_names = list(users.values())

def read_csv(csv_file):
    items = []
    if os.path.exists(csv_file):
        with open(csv_file, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                items.append(row)
    return items

def write_csv(csv_file, items):
    with open(csv_file, 'w', newline='') as file:
        fieldnames = ['name', 'availability', 'usage']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item)

# Routes
@app.route('/')
def index():
    # Fetch all items from the CSV file
    items = read_csv(csv_file)
    return render_template('index.html', items=items)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users:
        if username in admin_users and password == admin_users[username]:
            return redirect(url_for('admin_dashboard', username=users[username]))
        else:
            return redirect(url_for('user_dashboard', username=users[username]))
    else:
        return "Invalid username or password"

    # if username in users and users[username] == password:
    #     if username == 'user1':
    #         return redirect(url_for('admin_dashboard', username=users[username]))
    #     else:
    #         return redirect(url_for('user_dashboard', username=users[username]))
    # else:
    #     return "Invalid username or password"

@app.route('/admin/<username>')
def admin_dashboard(username):
    # Fetch all items from the CSV file
    items = read_csv(csv_file)
    return render_template('main.html', username=username, items=items, user_names=user_names)

@app.route('/user/<username>')
def user_dashboard(username):
    # Fetch all items from the CSV file
    items = read_csv(csv_file)
    return render_template('user.html', username=username, items=items)

@app.route('/add_item', methods=['POST'])
def add_item():
    username = request.args.get('username', '')
    name = request.form['name']
    availability = int(request.form['availability'])
    usage = request.form.get('usage', '')  # Usage is not included in the form anymore
    
    items = read_csv(csv_file)
    
    # Check if the item already exists in the inventory
    item_exists = False
    for item in items:
        if item['name'] == name:
            # If item exists, update the availability
            item['availability'] = str(int(item['availability']) + availability)
            item_exists = True
            break
    
    # If item does not exist, add it to the inventory
    if not item_exists:
        items.append({'name': name, 'availability': str(availability), 'usage': usage})
    
    write_csv(csv_file, items)
    
    return redirect(url_for('admin_dashboard', username=username))

@app.route('/remove_item', methods=['POST'])
def remove_item():
    username = request.args.get('username', 'Guest')
    name = request.form['name']

    items = read_csv(csv_file)
    items = [item for item in items if item['name'] != name]
    write_csv(csv_file, items)

    return redirect(url_for('admin_dashboard', username=username))

@app.route('/assign_item', methods=['POST'])
def assign_item():
    username = request.args.get('username', 'Guest')
    item_name = request.form['item_name']
    quantity = int(request.form['quantity'])
    assign_to = request.form['username']

    # Read the current inventory
    items = read_csv(csv_file)

    # Find the item in the inventory
    for item in items:
        if item['name'] == item_name:
            # Reduce the availability of the item
            item['availability'] = str(int(item['availability']) - quantity)

            # Update the 'usage' field
            if item['usage']:
                usages = item['usage'].split(', ')
                updated_usage = False
                for i, usage in enumerate(usages):
                    user, count = usage.split(' (')
                    count = int(count[:-1])
                    if user == assign_to:
                        usages[i] = f"{user} ({count + quantity})"
                        updated_usage = True
                        break
                if not updated_usage:
                    usages.append(f"{assign_to} ({quantity})")
                item['usage'] = ', '.join(usages)
            else:
                item['usage'] = f"{assign_to} ({quantity})"
            break

    # Write the updated inventory back to the CSV file
    write_csv(csv_file, items)

    # Return a JSON response indicating success
    return jsonify({'success': True})

@app.route('/return_item', methods=['POST'])
def return_item():
    item_name = request.form['item_name']
    quantity = int(request.form['quantity'])
    from_user = request.form['from_user']

    # Read the current inventory
    items = read_csv(csv_file)

    # Find the item in the inventory
    for item in items:
        if item['name'] == item_name:
            # Increase the availability of the item
            item['availability'] = str(int(item['availability']) + quantity)

            # Update the 'usage' field
            if item['usage']:
                usages = item['usage'].split(', ')
                updated_usage = False
                for i, usage in enumerate(usages):
                    user, count = usage.split(' (')
                    count = int(count[:-1])
                    if user == from_user:
                        count -= quantity
                        if count <= 0:
                            usages.pop(i)
                        else:
                            usages[i] = f"{user} ({count})"
                        updated_usage = True
                        break
                if not updated_usage:
                    # If the user is not found in the usage list, it means the user did not have any items assigned
                    # Hence, no need to update the usage
                    pass
                item['usage'] = ', '.join(usages)
            break

    # Write the updated inventory back to the CSV file
    write_csv(csv_file, items)

    # Return a JSON response indicating success
    return jsonify({'success': True})

@app.route('/request_item', methods=['POST'])
def request_item():
    # Extract data from the form submission
    requestby = request.form['from_user']
    item_name = request.form['item_name']
    quantity = int(request.form['quantity'])

    # Read the current inventory
    items = read_csv(request_file)

    # Add it to the request file
    items.append({'name': item_name, 'availability': str(quantity), 'usage': requestby})
    write_csv(request_file, items)

    # Return a JSON response indicating success
    return jsonify({'success': True})

# Route to handle fetching notification data
@app.route('/fetch_notifications')
def fetch_notifications():
    notifications = []
    # Read the CSV file
    with open(request_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Generate notification message
            if int(row['availability'])>0:
                notification_message = f"{row['usage']} requested to borrow {row['availability']} {row['name']}"
            if int(row['availability'])<0:
                notification_message = f"{row['usage']} requested to return {str(abs(int(row['availability'])))} {row['name']}"
            notifications.append(notification_message)
    return jsonify(notifications)

@app.route('/remove_notification', methods=['POST'])
def remove_notification():
    row_number = int(request.json.get('row_number', 0))

    # Read the current notifications from the CSV file
    notifications = read_csv(request_file)

    # Remove the notification from the list based on row number
    if 0 < row_number <= len(notifications):
        del notifications[row_number - 1]

        # Write the updated notifications back to the CSV file
        write_csv(request_file, notifications)

        # Return a JSON response indicating success
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Invalid row number'})

@app.route('/approve_notification', methods=['POST'])
def approve_notification():
    row_number = int(request.json.get('row_number', 0))

    # Read the current notifications from the CSV file
    notifications = read_csv(request_file)


    item_name = notifications[row_number - 1]['name']
    quantity = int(notifications[row_number - 1]['availability'])
    assign_to = notifications[row_number - 1]['usage']

    # Read the current inventory
    items = read_csv(csv_file)

    # Find the item in the inventory
    for item in items:
        if item['name'] == item_name:
            # Reduce the availability of the item
            item['availability'] = str(int(item['availability']) - quantity)

            # Update the 'usage' field
            if item['usage']:
                usages = item['usage'].split(', ')
                updated_usage = False
                for i, usage in enumerate(usages):
                    user, count = usage.split(' (')
                    count = int(count[:-1])
                    if user == assign_to:
                        usages[i] = f"{user} ({count + quantity})"
                        updated_usage = True
                        break
                if not updated_usage:
                    usages.append(f"{assign_to} ({quantity})")
                item['usage'] = ', '.join(usages)
            else:
                item['usage'] = f"{assign_to} ({quantity})"
            break

    # Write the updated inventory back to the CSV file
    write_csv(csv_file, items)

    # Remove the notification from the list based on row number
    if 0 < row_number <= len(notifications):
        del notifications[row_number - 1]

        # Write the updated notifications back to the CSV file
        write_csv(request_file, notifications)

        # Return a JSON response indicating success
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Invalid row number'})
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
