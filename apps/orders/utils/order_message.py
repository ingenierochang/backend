from urllib.parse import quote

def generate_order_message(order):
    items_message = ""
    for item in order.cart.items.all():
        product = item.product
        category_name = product.category.name if product.category else "Sin categoría"
        product_price_option_name = item.product_price_option.name if item.product_price_option else ""
        
        item_description = f"{category_name} - {product.name}"
        if product_price_option_name:
            item_description += f" - {product_price_option_name}"
        
        items_message += f"*· {item.quantity} {item_description}*\nValor: *${item.total_price:,.0f}*\n\n"

    message_parts = [
        f"Hola soy *{order.customer_full_name}*, me gustaría pedir para *{order.get_fulfillment_method_display().lower()}*:\n",
        f"\n{items_message}",
        f"*Subtotal: ${order.cart_total:,.0f}*",
        f"*Delivery: ${order.shipping_cost:,.0f}*\n",
        f"*Total: ${order.order_total:,.0f}*\n"
    ]

    if order.additional_instructions:
        message_parts.append(f"Mensaje: *{order.additional_instructions}*.\n")

    if order.customer_address:
        message_parts.append(f"Mi dirección es *{order.customer_address}*\n")

    if order.customer_commune:
        message_parts.append(f"Zona de despacho *{order.customer_commune}*\n")

    message_parts.extend([
        f"Mi número de contacto es *{order.customer_phone}*\n",
        f"Voy a pagar con *{order.get_payment_method_display()}*"
    ])

    message = "\n".join(message_parts)

    # Encode the message
    encoded_message = quote(message)
    return encoded_message