# numbers = [20, 10, 40, 30, 70, 90]
#     
# sum = 0
# for number in numbers:
#     sum += number
# 
# average = sum / len(numbers)
# print(average)

# numbers = [20, 10, 40, 30, 70, 90]
# 
# sum_numbers = 0
# count = 0
# 
# for num in numbers:
#     sum_numbers += num
#     count += 1
#     average = sum_numbers / count
#     print(f"Стъпка {count}: до тук числа {numbers[:count]} -> средно = {average}")
# 

numbers = [20, 10, 40, 30, 70, 90]

average = 0
count   = 0
for index in range(len(numbers)):
    average = (count * average + numbers[index]) / (count + 1)
    count += 1
    print(f"index = {index}, Стъпка {count}: до тук числа {numbers[:count]} -> средно = {average}")
