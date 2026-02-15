# ---------------- core/template_engine.py ----------------
class TemplateEngine:
    @staticmethod
    def render(sql_template, row_data):
        bind_vars = {k.upper():v for k,v in row_data.items()}
        return sql_template, bind_vars

