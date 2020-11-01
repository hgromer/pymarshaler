# Pymarshall - Marshall and Unmarshall Python Objects

## About
Pymarshall allows you to marshall and unmarshall any python object directly to and from a JSON formatted string. 

Pymarshall takes advantage of python's new [typing support](https://docs.python.org/3/library/typing.html). By reading class init param types, we are able to walk down nested JSON structures and assign appropriate values.

## Basic Usage

### Declare a class with typing information 

```python
class Test:

    def __init__(self, name: str):
        self.name = name
```

That's it! We can now marshall, and more importantly, unmarshall this object to and from JSON.

```python
from pymarshall import marshall
import json

test_instance = Test('foo')
blob = marshall.marshall(test_instance)
print(blob)
>>> '{name: foo}'

result = marshall.unmarshall(Test, json.loads(blob))
print(result.name)
>>> 'foo'
```

This is a pretty trivial example, lets add in a nested class

```python
class StoresTest:

    def __int__(self, test: Test):
        self.test = test

stores_test = StoresTest(Test('foo'))
blob = marshall.marshall(stores_test)
print(blob)
>>> '{test: {name: foo}}'

result = marshall.unmarshall(StoresTest, json.loads(blob))
print(result.test.name)
>>> 'foo'
```

As you can see, adding a nested class is as simple as as adding a basic structure.

## Advanced Usage

We can use pymarshall to handle containers as well. Again we take advantage of python's robust typing system

```python
from pymarshall import marshall
from typing import Set
import json

class TestContainer:
    
    def __int__(self, container: Set[str]):
        self.container = container

container_instance = TestContainer({'foo', 'bar'})        
blob = marshall.marshall(container_instance)
print(blob)
>>> '{container: ["foo", "bar"]}'

result = marshall.unmarshall(TestContainer, json.loads(blob))
print(result.container)
>>> '{foo, bar}'
```

Pymarshall can also handle containers that store user defined types. The `Set[str]` could easily have been `Set[UserDefinedType]`