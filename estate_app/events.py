import frappe;


def create_plots(doc, method):
    if method == "after_insert":
        no_of_plots = doc.get("no_of_plots")

        price_per_plot = doc.get("cash_price_per_plot")

        property_id = doc.get("name")

        if doc.name == property_id:
            print("--------------document -names")
            print(property_id)
            print(doc.name)
            if no_of_plots and price_per_plot:
                for index in range(no_of_plots):
                    if property_id == doc.name :
                        print("--------------document -names")
                        print(property_id)
                        print(doc.name)

                        plot_doc = frappe.new_doc("Plot")
                        plot_doc.parent = doc
                        plot_doc.parenttype = doc
                        plot_doc.parentfield = property_id
                        plot_doc.property_id = property_id
                        plot_doc.plot_no = index + 1
                        plot_doc.docstatus =  1
                        plot_doc.price = price_per_plot
                        plot_doc.state = "AVAILABLE"
                        plot_doc.block_no = f"to be severed from {doc.get('block_no')}"
                        plot_doc.insert(ignore_permissions=True)



@frappe.whitelist()
def get_plots(property_name):
    plots = frappe.get_all("Plot", filters={"property_id": property_name, "docstatus": 1},
                           fields=["name", "plot_no", "price", "state", "block_no"], order_by="plot_no")
    return plots


@frappe.whitelist(allow_guest=True)
def get_document(doctype, filters=None, fields=None):

    if filters is None:
        return frappe.get_all(doctype=doctype, fields=["*"])
    return frappe.get_all(doctype=doctype, filters=filters, fields=["*"])


# create a new leave application
@frappe.whitelist(allow_guest=True)
def new_leave_application(employee, from_date, to_date, leave_type, description, approver, half_day,
                          half_day_date=None):
    # Create a new leave application document
    try:
        leave_application = frappe.new_doc("Leave Application")

        # Set values for required fields
        leave_application.employee = employee
        leave_application.from_date = from_date
        leave_application.to_date = to_date
        leave_application.leave_type = leave_type
        leave_application.half_day = half_day
        leave_application.half_day_date = half_day_date
        leave_application.description = description
        leave_application.leave_approver = approver
        leave_application.insert(ignore_permissions=True)

        frappe.db.commit()

        # Send email notification
        send_leave_application_notification(leave_application)

        return {
            "message": "Leave Application Saved",
            "status": 201
        }
    except Exception as e:
        return {
            "message": str(e),
            "status": 422
        }


def send_leave_application_notification(leave_application):
    leave_application = frappe.get_doc("Leave Application", leave_application.name)
    # Construct email content
    subject = "Leave Application Submitted"
    message = f"Your leave application ({leave_application.name}) has been submitted successfully."

    # Get the employee's email address
    employee_email = frappe.get_value("Employee", leave_application.employee, "prefered_email")

    # Send the email
    frappe.sendmail(
        recipients=employee_email,
        subject=subject,
        message=message
    )
