# Pymarshaler - Marshal and Unmarshal Python Objects

## Disclaimer
This tool is in no way production ready

## About
Pymarshaler allows you to marshal and unmarshal any python object directly to and from a JSON formatted string. 

Pymarshaler takes advantage of python's new [typing support](https://docs.python.org/3/library/typing.html). By reading class init param types, we are able to walk down nested JSON structures and assign appropriate values.

## Basic Usage

### Declare a class with typing information 

Note, we can use regular old classes as long as their init methods are annotated properly, but it's preferable to use dataclasses whenever possible

```python
from dataclasses import dataclass

@dataclass
class Test:
    
    name: str
```

That's it! We can now marshal, and more importantly, unmarshal this object to and from JSON.

```python
from pymarshaler.marshal import Marshal
import json

test_instance = Test('foo')
blob = Marshal.marshal(test_instance)
print(blob.decode())
>>> '{name: foo}'

marshal = Marshal()
result = marshal.unmarshal(Test, json.loads(blob))
print(result.name)
>>> 'foo'
```

We also use `marshal.unmarshal_str(cls, str)` if we want to unmarshal directly from the blob source.

This is a pretty trivial example, lets add in a nested class

```python
from dataclasses import dataclass

@dataclass
class StoresTest:
    
    test: Test

    
stores_test = StoresTest(Test('foo'))
blob = marshal.marshal(stores_test)
print(blob)
>>> '{test: {name: foo}}'

result = marshal.unmarshal(StoresTest, json.loads(blob))
print(result.test.name)
>>> 'foo'
```

As you can see, adding a nested class is as simple as as adding a basic structure.

Pymarshaler will fail when encountering an unknown field by default, however you can configure it to ignore unknown fields

```python
from pymarshaler.marshal import Marshal 
from pymarshaler.arg_delegates import ArgBuilderFactory

marshal = Marshal()
blob = {'test': 'foo', 'unused_field': 'blah'}
result = marshal.unmarshal(Test, blob)
>>> 'Found unknown field (unused_field: blah). If you would like to skip unknown fields create a Marshal object who can skip ignore_unknown_fields'

marhsal = Marshal(ignore_unknown_fields=True)
result = marshal.unmarshal(Test, blob)
print(result.name)
>>> 'foo'
```

## Advanced Usage

We can use pymarshaler to handle containers as well. Again we take advantage of python's robust typing system

```python
from dataclasses import dataclass
from pymarshaler.marshal import Marshal
from typing import Set
import json

@dataclass
class TestContainer:
 
    container: Set[str]
    

marshal = Marshal()
container_instance = TestContainer({'foo', 'bar'})        
blob = marshal.marshal(container_instance)
print(blob.decode())
>>> '{container: ["foo", "bar"]}'

result = marshal.unmarshal(TestContainer,json.loads(blob))
print(result.container)
>>> '{foo, bar}'
```

Pymarshaler can also handle containers that store user defined types. The `Set[str]` could easily have been `Set[UserDefinedType]`

Pymarshaler also supports default values, and will use any default values supplied in the `__init__` if those values aren't present in the JSON data.

```python
from dataclasses import dataclass
from pymarshaler.marshal import Marshal

@dataclass
class TestWithDefault:
    
    name: str = 'foo'


marshal = Marshal()
result = marshal.unmarshal(TestWithDefault, {})
print(result.name)
>>> 'foo'
```
Pymarshaler will raise an error if any non-default attributes aren't given

Pymarshaler also supports a validate method on creation of the python object. This method will be called before being returned to the user.

```python
from dataclasses import dataclass
from pymarshaler.marshal import Marshal


@dataclass
class TestWithValidate:
    
    name: str

    def validate(self):
        print(f'My name is {self.name}!')


marshal = Marshal()
result = marshal.unmarshal(TestWithValidate, {'name': 'foo'})
>>> 'My name is foo!'
```

This can be used to validate the python object right at construction, potentially raising an error if any of the fields have invalid values

It's also possible to register your own custom unmarshaler for specific user defined classes by passing in a function pointer that will "resolve" the raw data

```python
from dataclasses import dataclass

from pymarshaler.marshal import Marshal


@dataclass
class ClassWithMessage:
    message: str


class ClassWithCustomDelegate:

    def __init__(self, message_obj: ClassWithMessage):
        self.message_obj = message_obj


def custom_delegate(data):
    return ClassWithCustomDelegate(ClassWithMessage(data['message']))


marshal = Marshal()
marshal.register_delegate(ClassWithCustomDelegate, custom_delegate)
result = marshal.unmarshal(ClassWithCustomDelegate, {'message': 'Hello from the custom delegate!'})
print(result.message_obj)
>>> 'Hello from the custom delegate!'
```

The result from any delegate should be the initialized resulting class instance

