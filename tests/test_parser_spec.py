from dofi.parser.spec import Spec


def test_foo(helper):
    path = helper.get_path("test_1.yaml")

    spec = Spec.from_yaml(path)
    print(spec.packages)
