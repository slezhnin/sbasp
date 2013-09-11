from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ColumnElement, _clause_element_as_expr


class rollup(ColumnElement):
    def __init__(self, element):
        self.element = _clause_element_as_expr(element)


@compiles(rollup, "mysql")
def _mysql_rollup(element, compiler, **kw):
    return "%s WITH ROLLUP" % (compiler.process(element.element, **kw))
