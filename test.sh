#!/usr/bin/bash

echo "SHOULD FAIL:"

for f in latte_tests/bad/*.lat; do echo $f && ./latc $f --silent; done

echo "SHOULD NOT FAIL:"

for f in latte_tests/good/*.lat
do
    echo $f && ./latc $f --silent --mrjp
done

# echo "PROBABLY SHOULD FAIL:"

# for f in mrjp-tests/bad/**/*.lat; do echo $f && ./latc $f --silent; done

# echo "PROBABLY SHOULD NOT FAIL:"

# for f in mrjp-tests/good/basic/*.lat
# do
#     echo $f && ./latc $f --silent --mrjp
# done
