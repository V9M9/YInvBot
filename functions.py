import pandas as pd

def inventarize(orders, inventory):
    orders = pd.read_excel(orders)
    inventory = pd.read_excel(inventory)

    orders['Места'] = orders['Места'].apply(lambda s: s.split(','))
    orders = orders.explode('Места')
    orders['Места'] = orders['Места'].str.strip()
    orders.reset_index(drop=True, inplace=True)

    inventory = inventory[['Номер заказа', 'Номер посылки']].rename(
        columns={'Номер посылки': 'Места', 'Номер заказа': 'Номер заказа(Инвент)'})
    orders = orders[['Номер заказа', 'Места']].rename(columns={'Номер заказа': 'Номер заказа(orders)'})

    real_inventarized = orders.merge(inventory, how='outer', on='Места')

    overc = real_inventarized['Номер заказа(orders)'].isna().sum()
    over_vals = real_inventarized[real_inventarized['Номер заказа(orders)'].isna()]['Места'].values

    shortage_count = real_inventarized['Номер заказа(Инвент)'].isna().sum()
    shortage_vals = real_inventarized[real_inventarized['Номер заказа(Инвент)'].isna()]['Места'].values

    newline = "\n"
    return (f""" Излишков {overc} шт: 
            Места: {newline.join(i for i in over_vals)}

Недостач {shortage_count} шт:
            Места: {newline.join(i for i in shortage_vals)} 
                
    """)

