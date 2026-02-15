# ---------------- core/staging.py ----------------
import uuid
from core.template_engine import TemplateEngine

class StagingManager:
    def __init__(self):
        self.staged_changes = []

    def stage_change(self, env, query_name, row_data, sql_template):
        sql, bind_vars = TemplateEngine.render(sql_template, row_data)
        staged_id = str(uuid.uuid4())
        self.staged_changes.append({
            'id': staged_id,
            'env': env,
            'query_name': query_name,
            'row_data': row_data,
            'sql_template': sql_template,
            'sql_generated': sql,
            'bind_vars': bind_vars,
            'include': True,
            'status': 'staged'
        })
        return staged_id

    def list_staged(self, query_name=None):
        return [s for s in self.staged_changes if query_name is None or s['query_name']==query_name]

    def toggle_row(self, staged_id, include=True):
        for s in self.staged_changes:
            if s['id']==staged_id:
                s['include'] = include
                break

    def commit_all(self, db_clients):
        for s in self.staged_changes:
            if not s['include']:
                continue
            client = db_clients.get(s['env'])
            if client:
                try:
                    client.execute_dml(s['sql_template'], s['bind_vars'])
                    client.commit()
                    s['status'] = 'committed'
                except Exception as e:
                    s['status'] = f'failed: {e}'
                    client.rollback()
                finally:
                    client.close_cursor()

    def revert_all(self, db_clients):
        for s in self.staged_changes:
            client = db_clients.get(s['env'])
            if client and s['status']=='committed':
                try:
                    row_data = s['row_data']
                    table = s['sql_template'].split()[1]  # naive table extraction
                    set_cols = [k for k in row_data.keys()]
                    revert_sql = f"UPDATE {table} SET " + ", ".join([f"{c} = :{c}" for c in set_cols]) + f" WHERE ROW_ID = :ROW_ID"
                    client.execute_dml(revert_sql, {k.upper():v for k,v in row_data.items()})
                    client.commit()
                    s['status']='reverted'
                except Exception as e:
                    s['status']=f'revert_failed: {e}'
                    client.rollback()
                finally:
                    client.close_cursor()
