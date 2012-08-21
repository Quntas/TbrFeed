<!DOCTYPE html>
<html lang="ja" itemscope itemtype="http://schema.org/WebApplication">
  <head>
    <meta charset="utf-8">
    <title>TbrFeed</title>
    <link rel="stylesheet" href="style.css">
    <meta name="keywords" content="Tumblr,フィード,RSS">
    <meta name="description" content="TbrFeedはTumblrのダッシュボードをRSSに変換するWebサービスです。">
    <meta name="author" content="azyobuzin">
    <meta itemprop="applicationCategory" content="Social">
    <meta itemprop="inLanguage" content="ja-JP">
    <meta property="og:title" content="TbrFeed" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="http://tbrfeed.azyobuzi.net/" />
    <script type="text/javascript">

      var _gaq = _gaq || [];
      _gaq.push(['_setAccount', 'UA-29400475-4']);
      _gaq.push(['_trackPageview']);

      (function() {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
      })();

    </script>
  </head>
  <body>
    <div id="header">
      <div id="header_content">
        <h1 id="title" itemprop="name">TbrFeed</h1>

    <?php
      require("tbrfeed.php");

      $id = $_COOKIE[$cookieKey];
      $loggedin = FALSE;
      $username;
      $uriBase;

      if ($id) {
        mysql_connect("localhost", $dbName, $dbPassword);
        mysql_select_db($dbName);
        mysql_set_charset('utf8');
        $sqlResult = mysql_query("SELECT id, username FROM " . $usersTable . " WHERE digest = '"
          . mysql_real_escape_string($id) . "'");
        $row = mysql_fetch_assoc($sqlResult);
        if ($row) {
          $loggedin = TRUE;
          $username = $row["username"];
          $uriBase = "feed.cgi/" . $id;

          mysql_query("UPDATE users SET last_access = now() WHERE id = " + $row["id"]);
        }
      }

      if ($loggedin) {
    ?>

        <div id="user">
          <?php print($username) ?>さん
          <a href="logout.cgi">ログアウト</a>
        </div>
        <div class="clear"></div>
      </div>
    </div>

    <div id="content">
      <h2>フィード RSS2.0</h2>
      <ul id="feeds">
        <li><a href="<?php print($uriBase) ?>">すべて</a></li>
        <li><a href="<?php print($uriBase) ?>/text">テキスト</a></li>
        <li><a href="<?php print($uriBase) ?>/photo">画像</a></li>
        <li><a href="<?php print($uriBase) ?>/quote">引用</a></li>
        <li><a href="<?php print($uriBase) ?>/link">リンク</a></li>
        <li><a href="<?php print($uriBase) ?>/chat">チャット</a></li>
        <li><a href="<?php print($uriBase) ?>/audio">音声</a></li>
        <li><a href="<?php print($uriBase) ?>/video">動画</a></li>
        <li><a href="<?php print($uriBase) ?>/answer">質問</a></li>
      </ul>

      <h2>利用停止</h2>
      <p>
        TbrFeedから、あなたのアカウントを削除し、フィードのURIを無効にします。
        Tumblrのアカウントは削除されません。
        ログインすれば再度利用することができます。
      </p>
      <form action="suspend.cgi" method="POST">
        <input type="hidden" name="id" value="<?php print($id) ?>">
        <button type="submit">利用停止</button>
      </form>
    </div>

    <?php
      } else {
    ?>

        <div id="user">
          <a href="authorize.cgi">ログイン</a>
        </div>
        <div class="clear"></div>
      </div>
    </div>

    <div id="content">
      <p itemprop="description">TbrFeedはTumblrのダッシュボードをRSSに変換するWebサービスです。</p>

      <h2>利用方法</h2>
      <p>
        ログイン後、次の中から購読したい投稿のタイプを選択して、煮るなり焼くなりしてください。<br>
        <img src="img/41042c.png" width="497" height="66" alt="スクリーンショット">
      </p>

      <h2>注意</h2>
      <ol>
        <li itemprop="browserRequirements">Cookieが有効になっていないとログインできません。</li>
        <li>TumblrのAPIの内容をそのままRSS2.0に変換しているだけなので、短時間に大量に取得すると、このサーバーとTumblrのサーバーに負担がかかります。</li>
      </ol>

      <h2>利用条件とプライバシーポリシー</h2>
      <ol>
        <li>本サービスは、Tumblrユーザーなら誰でもご利用いただけます。ただし、状況によってはご利用をお断りする場合があります。</li>
        <li>30日以上アクセスがない場合は、アカウントを一時停止させていただく場合があります。再度ログインすれば、またご利用いただけます。</li>
        <li>作者は本サービスを利用したことによる損害の責任を一切負わないものとします。</li>
        <li>作者は利用者の情報管理にできるだけ努力しますが、障害が起こってしまった場合でも責任は一切負いません。</li>
      </ol>

      <h2>利用開始</h2>
      <form action="authorize.cgi" method="GET">
        <button type="submit">Sign in with Tumblr</button>
      </form>

      <h2>お問い合わせ</h2>
      <p>
        要望・不具合報告は、Twitter <a href="https://twitter.com/intent/tweet?screen_name=azyobuzin" class="twlink">@azyobuzin</a> までお願いします。<br>
        あと、 <a href="https://twitter.com/intent/tweet?button_hashtag=tbrfeed" class="twlink">#tbrfeed</a> タグをつけてツイートすれば見たり見なかったりします。
      </p>

      <h2>オープンソースプロジェクト</h2>
      <p>ソースコードを<a href="https://github.com/azyobuzin/TbrFeed">GitHub</a>で公開しています。</p>

      <h2>使用ライブラリ</h2>
      <p>TbrFeedは、PythonとPHPを用いて開発されており、以下の外部ライブラリを使用しています。</p>
      <ul>
        <li><a href="https://github.com/simplegeo/python-oauth2">python-oauth2</a></li>
        <li><a href="http://mysql-python.sourceforge.net/">MySQL-Python</a></li>
        <li><a href="http://labix.org/python-dateutil/">python-dateutil</a></li>
        <li><a href="https://bitbucket.org/bbangert/webhelpers/overview">WebHelpers</a></li>
      </ul>
    </div>

    <?php
      }
    ?>

    <div id="footer">
      <div id="share">
        <div class="ninja_onebutton">
        <script type="text/javascript">
        //<![CDATA[
        (function(d){
        if(typeof(window.NINJA_CO_JP_ONETAG_BUTTON_1471dc00a589fb57b6d60531c8ecd0d8)=='undefined'){
            document.write("<sc"+"ript type='text\/javascript' src='http:\/\/omt.shinobi.jp\/b\/1471dc00a589fb57b6d60531c8ecd0d8'><\/sc"+"ript>");
        }else{
            window.NINJA_CO_JP_ONETAG_BUTTON_1471dc00a589fb57b6d60531c8ecd0d8.ONETAGButton_Load();}
        })(document);
        //]]>
        </script><span class="ninja_onebutton_hidden" style="display:none;"></span><span style="display:none;" class="ninja_onebutton_hidden"></span>
        </div>
      </div>
      <div id="copyright">
        ©<span itemprop="copyrightYear">2012</span>
        <span itemprop="copyrightHolder author" itemscope itemtype="http://schema.org/Person"><a itemprop="name url" href="http://www.azyobuzi.net/">azyobuzin</a></span>,
        Special thanks <span itemprop="contributor" itemscope itemtype="http://schema.org/Person"><a itemprop="name url" href="http://yut.ifdef.jp/">yut831</a></span>
      </div>
    </div>
  </body>
</html>
