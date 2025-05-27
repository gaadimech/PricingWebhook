import json
import os

def update_ev_dent_paint_prices():
    """
    Reduce dent_paint price by 500 rs for all EV vehicles in pricing_data.json
    """
    # Read the current pricing data
    with open('pricing_data.json', 'r') as file:
        data = json.load(file)
    
    # Check if EV section exists
    if 'EV' not in data['data']:
        print("No EV section found in the data")
        return
    
    ev_data = data['data']['EV']
    updated_count = 0
    
    # Iterate through all brands in EV section
    for brand_name, brand_data in ev_data.items():
        print(f"Processing brand: {brand_name}")
        
        # Iterate through all models in the brand
        for model_name, model_data in brand_data.items():
            if 'dent_paint' in model_data and model_data['dent_paint'] is not None:
                old_price = model_data['dent_paint']
                new_price = old_price - 500
                
                # Ensure price doesn't go below 0
                if new_price < 0:
                    new_price = 0
                
                model_data['dent_paint'] = new_price
                updated_count += 1
                
                print(f"  {model_name}: {old_price} -> {new_price}")
            else:
                print(f"  {model_name}: No dent_paint price or null value")
    
    # Create backup of original file
    if not os.path.exists('pricing_data_backup.json'):
        with open('pricing_data_backup.json', 'w') as backup_file:
            json.dump(data, backup_file)
        print("Backup created: pricing_data_backup.json")
    
    # Write updated data back to file
    with open('pricing_data.json', 'w') as file:
        json.dump(data, file)
    
    print(f"\nUpdate completed! {updated_count} EV vehicles had their dent_paint prices reduced by 500 rs.")
    print("Updated pricing_data.json file saved.")

if __name__ == "__main__":
    update_ev_dent_paint_prices() 