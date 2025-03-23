from flask import Flask, render_template, request
import pickle
import pandas as pd

app = Flask(__name__)

# Load the model and data from the pickle file
with open("data.pkl", "rb") as f:
    data = pickle.load(f)

columns = data["columns"]
model = data["model"]
name = data["res_name"]
location = data["location"]
rest_type = data["rest_type"]
cuisines = data["cuisines"]

@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None

    if request.method == "POST":
        location_input = request.form.get("location")
        online_order = request.form.get("online_order")
        table_booking = request.form.get("table_booking")
        rest_type_input = request.form.getlist("rest_type")  # Multiple selection
        cuisines_input = request.form.getlist("cuisines")
        votes = request.form.get("votes")
        approx_cost = request.form.get("approx_cost")

        # Initialize data dictionary with zeros for all expected columns
        data_dict = {col: 0 for col in columns}  

        if location_input in data_dict:
            data_dict[location_input] = 1
        if online_order == "Yes":
            data_dict['online_order'] = 1
        if table_booking == "Yes":
            data_dict['book_table'] = 1

        try:
            data_dict['votes'] = int(votes) if votes else 0
            data_dict['approx_cost'] = float(approx_cost) if approx_cost else 0
        except ValueError:
            return render_template("index.html", prediction="Invalid input. Please enter valid numbers.",
                                   name=name, location=location, rest_type=rest_type, cuisines=cuisines,
                                   location_selected=location_input, online_order_selected=online_order,
                                   table_booking_selected=table_booking, rest_type_selected=rest_type_input,
                                   cuisines_selected=cuisines_input, votes=votes, approx_cost=approx_cost)

        for rt in rest_type_input:
            if rt in data_dict:
                data_dict[rt] = 1

        for cui in cuisines_input:
            if cui in data_dict:
                data_dict[cui] = 1

        # Ensure dataframe matches trained model's feature names
        df = pd.DataFrame([data_dict])[columns]  

        # Predict rating
        prediction = round(model.predict(df)[0], 2)

        return render_template("index.html", prediction=prediction, 
                               name=name, location=location, rest_type=rest_type, cuisines=cuisines,
                               location_selected=location_input, online_order_selected=online_order,
                               table_booking_selected=table_booking, rest_type_selected=rest_type_input,
                               cuisines_selected=cuisines_input, votes=votes, approx_cost=approx_cost)

    return render_template("index.html", name=name, location=location, rest_type=rest_type, cuisines=cuisines)
if __name__ == "__main__":
    app.run(debug=True)
