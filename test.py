beforeLine="This division of labour, from which so many advantages are derived, is not originally the effect of any human wisdom, which foresees and intends that general opulence to which it gives occasion. It is the necessary, though very slow and gradual, consequence*** of a certain propensity in-human nature\which has in view no such extensive utility; the propensity to truck, barter, and exchange one thing for another."

to_find_string=beforeLine.replace(",","").replace("."," ").replace("\""," ").replace("\'"," ").replace(";"," ").replace("-"," ").replace("*"," ").replace("\\"," ").lower()

print (to_find_string)