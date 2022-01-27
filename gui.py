import PySimpleGUI as sg
import system
width, height = sg.Window.get_screen_size()
print(width, height)
sys = system.System()


list_font = ("Helvetica", 30)
text_font = ('Helvetica', 30)

one_third_size = (25, 20)

user_strings = [element.strip("'") for element in sys.users.keys()]
user_list = sg.Listbox(values=user_strings, size=one_third_size, key='-selected_user-', font=list_font, change_submits=True)

item_strings = [element.strip("'") for element in sys.return_stocked_items()]
item_list = sg.Listbox(values=item_strings, size=one_third_size, key='-selected_item-', font=list_font, change_submits=True)

item_amount_box = sg.Text('Menge Konsumiert: ', size=(20, 5), key='-items_consumed-', font=text_font)
credit_box = sg.Text('Guthaben: ', size=(20, 5), key='-credit-', font=text_font)
price_box = sg.Text('Preis: ', size=(20, 5), key='-price-', font=text_font)

output_box = sg.Text('Guthaben: /\nPreis: /', size=(4, 5), key='-output-', font=text_font, text_color='black')
striche_box = sg.Text('Striche: ', key='-striche-', font=('Helvetica', 11))
add_button = sg.Button('Bitte Person und Item auswählen', key='-Add-', size=(25, 1), font=list_font)

layout = [[sg.Column([[user_list]]), sg.Column([[item_list]]), sg.Column([[output_box, add_button, striche_box]])]]

window = sg.Window('Item System', layout, size=(width, height), background_color='white')

while True:  # Event Loop
    event, values = window.Read()
    print(event, values)

    def update_essentials():
        consumed = None
        credit = None
        price = None

        if len(values['-selected_user-']) >= 1 and len(values['-selected_item-']) >= 1:
            user = values['-selected_user-'][0]
            item = values['-selected_item-'][0]
            consumed = sys.users[user]['items'].get(item) if sys.users[user]['items'].get(item) is not None else 0
            window['-Add-'].update(f'1 mal "{item}" zu {user} hinzufügen')
        else:
            window['-Add-'].update(f'Bitte Person und Item auswählen')
        if len(values['-selected_user-']) >= 1:
            user = values['-selected_user-'][0]
            credit = sys.users[user]['credit']
        if len(values['-selected_item-']) >= 1:
            item = values['-selected_item-'][0]
            price = sys.items[item]['price']
        counter = 0
        striche_string = ''
        if consumed is not None:
            if counter%5 == 0:
                striche_string += ' '
            striche_string += '|'
            counter += 1
        window['-striche-'].update(f'Striche: {striche_string if consumed is not None else ""}')
        window['-output-'].update(f'Guthaben: {str(credit)+"€" if credit is not None else "/"}\nPreis: {str(price)+"€" if price is not None else "/"}')

    if event == sg.WIN_CLOSED:
        break
    if event == '-Add-':
        if len(values['-selected_user-']) >= 1 and len(values['-selected_item-']) >= 1:
            user = values['-selected_user-'][0]
            item = values['-selected_item-'][0]

            sys.consume_item(user, item, 1)
            window['-selected_item-'].update(values=sys.return_stocked_items())
            window['-selected_user-'].update(values=[element.strip("'") for element in sys.users.keys()])

            values['-selected_user-'] = ''
            values['-selected_item-'] = ''

            update_essentials()

    if event == '-Show-':
        print(values['-selected_user-'], values['-selected_item-'])

    if event == '-selected_item-' or event == '-selected_user-':
        update_essentials()



window.close()