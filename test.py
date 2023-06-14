def hand_cards_calculate(cards: list) -> int:
    card_A_amount = 0  # A卡的數量
    replace_cards = []  # 清理過的卡牌格式
    for card in cards:
        if card == 1:  # 這張卡是A
            card_A_amount += 1  # A卡計數增加
        if card >= 10:  # 10,11,12都當做10計算
            replace_cards.append(10)
        else:
            replace_cards.append(card)  # 加入卡牌
    card_total = sum(replace_cards)
    if card_A_amount and card_total <= 11:  # 有A牌 and 牌夠小
        card_total += 10  # 把1(A)當作11，所以要加10
    return card_total


print(hand_cards_calculate([1, 11]))
