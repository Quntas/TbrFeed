# TbrFeed #
[http://tbrfeed.azyobuzi.net/](http://tbrfeed.azyobuzi.net/) のソースコードです。

# ソースコード中に書いていない補足
データベースは PostgreSQL を使用しています。そのなかでふたつ独自に定義した関数があります。

## update_lastaccess
```sql
CREATE OR REPLACE FUNCTION update_lastaccess(m_id character)
  RETURNS void AS
'UPDATE users SET lastaccess = NOW() WHERE id = m_id;'
  LANGUAGE sql VOLATILE
  COST 100;
```

## update_user
```sql
CREATE OR REPLACE FUNCTION update_user(m_id text, m_username text, m_token text, m_secret text)
  RETURNS text AS
$BODY$
DECLARE
	ret_id text;
BEGIN
	UPDATE users SET token = m_token, secret = m_secret, lastaccess = NOW() WHERE username = m_username;
	IF found THEN
		SELECT id INTO ret_id FROM users WHERE username = m_username;
		RETURN ret_id;
	ELSE
		INSERT INTO users VALUES (m_id, m_username, m_token, m_secret, NOW(), NOW());
		RETURN m_id;
	END IF;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
```
