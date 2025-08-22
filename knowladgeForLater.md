# Project Knowledge Notes

## JSON
- JSON supports: object, array, string, number, boolean, null.
- Python tuples serialize as JSON arrays; on load they become lists. Need manual conversion if tuple semantics required.

### JSON Serialization Patterns (Multiple Inheritance & Mixins)
- Cooperative pattern: every mixin/base that participates implements load() and to_dict(), and inside each calls super().load(...) / super().to_dict() in a try/except AttributeError (or uses hasattr) to stay MRO-safe.
- Always merge dictionaries instead of overwriting: start with parent payload (base = dict(super().to_dict())) before adding own keys.
- Add a "__type__" (or similar) discriminator in the serialized dict so generic factory code can re-instantiate the correct class.
- Use an explicit class registry (decorator @register_game_object) instead of globals() to map "__type__" -> class. Safer and decouples import order (just ensure modules are imported so registration runs).
- Keep __init__ minimal (establish default empty / neutral state); perform full population in load(). This allows constructing subclasses in generic deserialization without needing complex argument plumbing.
- from_json: parse JSON -> dict, resolve class via "__type__", instantiate with minimal ctor, then call load().
- Deterministic structure: convert internal tuples back to lists when serializing (JSON-friendly) and re-tuple on load for immutability expectations.
- When serializing graphs (e.g. connections) prefer referencing related objects by stable identifiers (ids) instead of embedding full objects to avoid recursion / duplication; reconstruct links in a second pass.
- Order of base classes matters: put data-bearing bases before behavior-only mixins if latter rely on attributes set by earlier bases (affects MRO resolution of load()/to_dict()).
- Defensive loading: tolerate absent keys via dict.get defaults; elevate to explicit errors only for truly required fields.
- Validation descriptors: if you want them enforced during deserialization, assign through normal attribute setting inside load(); if you bypass (e.g. writing directly to __dict__), you skip validation—do this only intentionally.

## Object References & Mutability
- Python variables hold references (names -> objects). Assignment rebinds the name; it does not mutate the object.
- del name removes the binding; object is collected when no refs remain.
- Lists and tuples both store references (not inline data). Difference: list is mutable/resizable; tuple has fixed size & immutable slots.
- Tuples are immutable containers of references; contained mutable objects can still change.

## Argument Passing
- Function arguments are passed by object reference (call-by-sharing). Tuples are not copied on pass.
- Cannot in-place modify a tuple; rebinding creates a new tuple object. Other holders keep old one.

## When Shared Mutation Needed
- Use a mutable structure (list, dict, custom small class) to share changing state instead of a tuple.
- Wrapper pattern example:
  - Create a class holding a list (e.g. coords) with properties x/y and mutate that.

## Shallow vs Deep Copies
- list.copy(), slicing, tuple(...), etc. create new containers with same element references (shallow).
- Multiplying lists (e.g. [[]] * 3) repeats the same inner reference.

## Descriptors
- __get__, __set__, __delete__ only trigger when the descriptor is a class attribute accessed via instance/class.
- Naming a method __set__ inside a normal (non‑descriptor) object does nothing for rebinding external variables.
- Correct __set__ signature: def __set__(self, instance, value).
- Validation descriptors: instantiate them (x = PositiveInt()) – assigning the class (x = PositiveInt) disables descriptor behavior.

### Attribute Lookup & Descriptor Precedence
Full (simplified) algorithm for obj.attr (object.__getattribute__):
1. Resolve attr on the class MRO (type(obj).__mro__) -> attr_obj (first hit).
2. If attr_obj is a data descriptor (defines __set__ or __delete__):
   - If it has __get__, return attr_obj.__get__(obj, type(obj)) immediately (instance __dict__ is ignored).
3. Else, look in obj.__dict__; if present, return that value.
4. If attr_obj was found:
   - If it is a non‑data descriptor (has __get__ but no __set__/__delete__), return attr_obj.__get__(obj, type(obj)).
   - Else return attr_obj (plain value / function; functions become bound methods via their own descriptor).
5. Else, if class defines __getattr__, call it; otherwise raise AttributeError.
Write precedence (obj.attr = value):
- If class has a data descriptor with __set__, call it.
- Else store in obj.__dict__[attr].
Delete precedence (del obj.attr):
- If data descriptor has __delete__, call it; else remove from obj.__dict__; else AttributeError.
Data descriptor > instance __dict__ > non‑data descriptor / plain class attribute > __getattr__ fallback.
Practical effects:
- @property produces a data descriptor; it overrides an instance attribute with same name.
- Plain methods (only __get__) are non‑data; an instance attribute of same name shadows the method.
- A descriptor with __set__ but no __get__ still intercepts writes, but reads fall through to instance __dict__, so validation occurs only on assignment; later reads bypass the descriptor.

### Consistent Descriptor Design
- Do not mix a @classmethod check in a base with an instance-method override in a subclass if you rely on super().check: super() resolution for classmethods will call the next attribute as an unbound function expecting the class, not an instance.
- Pick one style (all classmethods, or all instance methods). Instance methods + class-level configuration accessed via type(self) are often clearer.
- Provide __get__ if you need read mediation; otherwise writes validate once and subsequent reads bypass logic.

### Safe Validation “Compute Then Commit”
Pattern to avoid partial state on exceptions:
```
def set_resource(self, raw):
    # 1. Derive candidate
    new_value = build(raw)
    # 2. Validate fully
    validate(new_value)
    # 3. Commit atomically
    self._value = new_value
```
Never mutate current state before finishing validation (prevents inconsistent objects if an error is raised mid-way).

## Immutable Wrapper Pattern (Texture)
- Provide read-only sequence interface; expose explicit update method instead of item assignment.
- Prevent misleading partial mutation attempts; raise clear TypeError in __setitem__.

### Copy vs Reference in Immutability
- Wrapping mutable inputs (like list[str]) into an immutable tuple copy shields internal state.
- Expose only read operations; updates go through a method that constructs & validates a new immutable snapshot before assignment.

## Object References & Mutability
- Python variables hold references (names -> objects). Assignment rebinds the name; it does not mutate the object.
- del name removes the binding; object is collected when no refs remain.
- Lists and tuples both store references (not inline data). Difference: list is mutable/resizable; tuple has fixed size & immutable slots.
- Tuples are immutable containers of references; contained mutable objects can still change.

### Iterables, Iterators, Generators
- Iterable: object implementing __iter__ returning an iterator (e.g. list, tuple, dict, generator).
- Iterator: object implementing __iter__ (returning self) and __next__ (stateful, one-pass).
- Generator function: a def containing yield; calling it returns a generator object (an iterator).
- Generator expression: (expr for x in iterable) produces a generator (iterator).
- All generators are iterators; not all iterables are iterators (list != iter(list())).
Implication: Don’t reuse a generator after exhaustion; create a fresh one instead.

## Argument Passing
- Function arguments are passed by object reference (call-by-sharing). Tuples are not copied on pass.
- Cannot in-place modify a tuple; rebinding creates a new tuple object. Other holders keep old one.

## When Shared Mutation Needed
- Use a mutable structure (list, dict, custom small class) to share changing state instead of a tuple.
- Wrapper pattern example:
  - Create a class holding a list (e.g. coords) with properties x/y and mutate that.

## Shallow vs Deep Copies
- list.copy(), slicing, tuple(...), etc. create new containers with same element references (shallow).
- Multiplying lists (e.g. [[]] * 3) repeats the same inner reference.

## Attribute Lookup & Mental Model (Refresher)
- Name binding: identifier -> object (refcount increments).
- Rebinding changes the name’s target; it does not “update” existing references.
- del name removes binding; object collected when refcount hits zero (or later by GC for cyclic containers).

## Structural Pattern Matching (Python 3.10+)
Use match/case instead of long if/elif chains for:
- Literal / enum matching:
  ```
  match code:
      case 200: ...
      case 400 | 404: ...
      case _: ...
  ```
- Sequence & destructuring:
  ```
  match point:
      case (0, 0): ...
      case (x, 0): ...
      case (0, y): ...
      case (x, y) if x == y: ...
  ```
- Class patterns leverage __match_args__ or keyword attributes:
  ```
  match obj:
      case Position2D(x=0, y=y): ...
      case Position2D(x=x, y=y) if x > y: ...
  ```
Principles: patterns bind names (not test equality) unless they are literals; use guards (if) for extra conditions.

## Validators (custom descriptors)
- Base Validator uses __set_name__ and __set__ to validate on attribute assignment.
- Typed / PositiveInt / RectangularStringTuple chain validations using classmethod check().
- Remember to instantiate descriptor: _y = PositiveInt() not _y = PositiveInt.

### Descriptor Storage Naming
- Use a private storage name inside __set_name__: self.storage = f"_{public_name}" to avoid clashes and ensure consistent mediation (especially when adding __get__).

## Common Pitfalls Observed
- Rebinding a variable (tex = "bb") does not invoke methods on the prior object.
- Attempting tuple/list immutability enforcement by relying on underlying tuple errors is unclear; better to raise custom error.
- Size/shape validation: ensure rectangular data and size consistency at construction/update.
- Assigning through descriptor name inside __init__ may overwrite descriptor if you directly set self.__class__.attr; always assign on the instance (self.attr = value) so descriptor __set__ triggers.
- Returning partially validated state when an exception occurs leads to hard-to-debug inconsistencies; use compute-then-commit.

## Quick Mental Models
- Name binding: name -> object -> (type, refcount, value).
- list = mutable array of PyObject*; tuple = fixed array of PyObject*.
- Immutability applies to container structure, not transitively to contained objects.

## Object Construction (__new__ vs __init__)
- __new__(cls, *args) allocates & returns the new instance (for immutable / customizing allocation).
- __init__(self, *args) initializes already-created instance; returning value is ignored (must return None).
- Override __new__ when:
  - Subclassing immutable built-ins (tuple, str, int) and needing to influence creation.
  - Implementing singletons / caching / flyweight patterns.
Instrumentation:
```
class X:
    def __new__(cls, *a, **k):
        print("alloc", cls)
        return super().__new__(cls)
    def __init__(self, *a, **k):
        print("init", self)
```

## Debugging & Tooling
- Run a module under the built‑in debugger: python -m pdb package.module (uses module resolution); OR python -m pdb path/to/file.py.
- Set breakpoint in code: import pdb; pdb.set_trace() (avoid leaving in committed code).
- Use c (continue), n (next), s (step into), l (list), p expr, q (quit) for core pdb navigation.

## Advanced Type Hinting Patterns
- Callable bound methods: A bound method of an instance with no parameters can be annotated as Callable[[], ReturnType].
- Protocol for structural typing (preferred when expecting any object with a render method):
  class Renderable(Protocol):
      def render(self) -> tuple[tuple[int,int], list[str], tuple[int,int]]: ...
  def draw_element(fn: Callable[[], RenderReturn]): ...
  Accepts any object whose render matches the signature; no inheritance required.
- TypeVar constrained to a base:
  TGameObj = TypeVar("TGameObj", bound="GameObject")
  def draw_element(obj: TGameObj): obj.render()
  Ensures obj is a GameObject subclass while preserving subtype return covariance.
- Return type reuse: define RenderReturn = tuple[tuple[int,int], list[str], tuple[int,int]] to keep signatures DRY.
- Prefer Protocol over isinstance checks to reduce coupling and enable easier testing/mocking.
