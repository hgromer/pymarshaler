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

result = marshall.unmarshall(Test,json.loads(blob))
print(result.name)
>>> 'foo'
```

We also use `marshall.unmarshall_str(cls, str)` if we want to unmarshall directly from the blob source.

This is a pretty trivial example, lets add in a nested class

```python
class StoresTest:

    def __int__(self, test: Test):
        self.test = test

stores_test = StoresTest(Test('foo'))
blob = marshall.marshall(stores_test)
print(blob)
>>> '{test: {name: foo}}'

result = marshall.unmarshall(StoresTest,json.loads(blob))
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

result = marshall.unmarshall(TestContainer,json.loads(blob))
print(result.container)
>>> '{foo, bar}'
```

Pymarshall can also handle containers that store user defined types. The `Set[str]` could easily have been `Set[UserDefinedType]`

Pymarshall also supports default values, and will use any default values supplied in the `__init__` if those values aren't present in the JSON data.

```python
from pymarshall import marshall

class TestWithDefault:

    def __init__(self, name: str = 'foo'):
        self.name = name

result = marshall.unmarshall(TestWithDefault, {})
print(result.name)
>>> 'foo'
```
Pymarshall will raise an error if any non-default attributes aren't given

Pymarshall also supports a validate method on creation of the python object. This method will be called before being returned to the user.

```python
from pymarshall import marshall

class TestWithValidate:

    def __init__(self, name: str):
        self.name = name

    def validate(self):
        print(f'My name is {self.name}!')


result = marshall.unmarshall(TestWithValidate, {'name': 'foo'})
>>> 'My name is foo!'
```

This can be used to validate the python object right at construction, potentially raising an error if any of the fields have invalid values

It's also possible to register your own customer unmarshaller for specific user defined classes.

```python
from pymarshall.arg_delegates import ArgBuilderDelegate, ArgBuilderFactory
from pymarshall import marshall


class ClassWithMessage:
    
    def __init__(self, message: str):
        self.message = message


class ClassWithCustomDelegate:

    def __init__(self, message_obj: ClassWithMessage):
        self.message_obj = message_obj


class CustomDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        super().__init__(cls)

    def resolve(self, data):
        return {'message_obj': ClassWithMessage(data['message'])}


ArgBuilderFactory.register_delegate(ClassWithCustomDelegate, CustomDelegate)
result = marshall.unmarshall(ClassWithCustomDelegate, {'message': 'Hello from the custom delegate!'})
print(result.message_obj)
>>> 'Hello from the custom delegate!'
```

The result from any delegate should be a dictionary, however any data inside the returned dictionary should be in their class form. 

