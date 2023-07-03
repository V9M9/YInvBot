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
    over_vals = real_inventarized[real_inventarized['Номер заказа(orders)'].isna()][
        ['Номер заказа(Инвент)', 'Места']].to_string(index=False, col_space=25)

    shortage_count = real_inventarized['Номер заказа(Инвент)'].isna().sum()
    shortage_vals = real_inventarized[real_inventarized['Номер заказа(Инвент)'].isna()][['Номер заказа(orders)' ,'Места']].to_string(index=False, col_space=25)

    if overc == 0 and shortage_count == 0:
        return "Всё сошлось! Ты молодец!😉🥳"

    return (f""" Излишков {overc} шт: 
<b>{over_vals if overc > 0 else ""}</b>

Недостач {shortage_count} шт:
<b>{shortage_vals if shortage_count > 0 else ""}</b>
                
    """)
