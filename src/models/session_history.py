from sqlalchemy.sql.ddl import DDL
import enum


class DeviceType(enum.Enum):
    PC = 'pc'
    TABLET = 'tablet'
    MOBILE = 'mobile'
    BOT = 'bot'
    UNKNOWN = 'unknown'


def create_table_login_history_partition_ddl(
    table: str,
    device_type: DeviceType
) -> DDL:
    return DDL(
        """
        CREATE TABLE IF NOT EXISTS %s
        PARTITION OF session_history FOR VALUES IN ('%s');
        """
        % (table, device_type.value)
    ).execute_if(dialect="postgresql")
