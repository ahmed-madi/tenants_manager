
parse_menu_text =  """
    Analyze the provided images of a restaurant menu and extract detailed information about the menu items.
    For each category on the menu, extract the following details for each item (if field data is not available return empty string):

    1. Title: The name of the menu item.
    2. Price: The price of the menu item. Value type: float.
    3. Currency: The currency code of the menu item (e.g., USD, EUR).
    4. Description: A description of the menu item.
    5. Ingredients: List of raw materials or components used to create a dish, if available. Provide only ingredients which are mentioned in menu item name and description.
    6. Calories: If available, provide the calorie count. Value type: integer.
    7. Allergies: List of allergens if provided (e.g., gluten, nuts, dairy).
    8. Variations: List of variations: Any additional charges or modifications to the price for different customizations (e.g., "extra toppings", "substitute for extra side")
    
    Provide every item.
    Return the data in JSON string in one line without line breaks using the following structure:

    {
      "items": [
            {
              "category": "Category Name",
              "title": "Item Name",
              "price": "Item Price",
              "currency": "Item Currency",
              "description": "Item Description",
              "ingredients": ["Ingredient 1", "Ingredient 2", "..."],
              "calories": "Calories (if available)",
              "allergies": ["Allergen 1", "Allergen 2", "..."],
              "variations": [
                        {
                            "name": "Variation 1",
                            "price": "Variation 1 Price"
                        },
                        {
                            "name": "Variation 2",
                            "price": "Variation 2 Price"
                        }
                ]
            },
            {
              "category": "Another Category Name",
              "title": "Another Item Name",
              "price": "Another Item Price",
              "currency": "Another Item Currency",
              "description": "Another Item Description",
              "ingredients": ["Another Ingredient 1", "Another Ingredient 2", "..."],
              "calories": "Another Calories (if available)",
              "allergies": ["Another Allergen 1", "Another Allergen 2", "..."],
              "variations": [
                        {
                            "name": "Another Variation 1",
                            "price": "Another Variation 1 Price"
                        },
                        {
                            "name": "Another Variation 2",
                            "price": "Another Variation 2 Price"
                        }
                    ]
            }
      ]
    }
"""