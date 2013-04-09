#!/virtual/azyobuzin/local/bin/python
# -*- coding: utf-8 -*-

import cgitb
cgitb.enable()

import session

with session.Session() as sess:
    loggedin = "user" in sess.data
    uribase = "feed/" + sess.data["user"][0] if loggedin else None

    print sess.cookie
    print "Content-Type: text/html; charset=utf-8"
    print """
<!DOCTYPE html>
<html version="HTML+RDFa 1.1" lang="ja-JP" xmlns:og="http://ogp.me/ns#" itemscope itemtype="http://schema.org/WebPage">
    <head>
        <meta charset="utf-8" />
        <title itemprop="name">TbrFeed - Tumblr のダッシュボードを RSS で出力</title>
        <link rel="stylesheet" href="style.css" />
        <meta name="keywords" content="Tumblr,フィード,RSS" />
        <meta name="description" content="Tumblr のダッシュボードを RSS に変換します。" />
        <meta name="author" content="http://twitter.com/azyobuzin" />
        <meta property="og:title" content="TbrFeed - Tumblr のダッシュボードを RSS で出力" />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="http://tbrfeed.azyobuzi.net/" />
        <meta property="og:site_name" content="TbrFeed" />
        <meta property="og:description" content="Tumblr のダッシュボードを RSS に変換します。" />
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
        <div id="fb-root"></div>
        <script>(function(d, s, id) {
          var js, fjs = d.getElementsByTagName(s)[0];
          if (d.getElementById(id)) return;
          js = d.createElement(s); js.id = id;
          js.src = "//connect.facebook.net/ja_JP/all.js#xfbml=1";
          fjs.parentNode.insertBefore(js, fjs);
        }(document, 'script', 'facebook-jssdk'));</script>

        <div id="header" itemscope itemtype="http://schema.org/WPHeader">
            <div id="header_content">
                <h1 id="title">TbrFeed</h1>
                <div id="followtumblr"><iframe class="btn" frameborder="0" border="0" scrolling="no" allowtransparency="true" height="25" width="138" src="http://platform.tumblr.com/v1/follow_button.html?button_type=1&amp;tumblelog=tbrfeed&amp;color_scheme=dark"></iframe></div>
                <div id="user">
                    """ + (sess.data["user"][1] + """さん <a href="logout.cgi">ログアウト</a>""" if loggedin else """<a href="authorize.cgi">ログイン</a>""") + """
                </div>
                <div class="clear"></div>
            </div>
        </div>

        <div id="ad_header">
            <!-- admax -->
            <script type="text/javascript" src="http://adm.shinobi.jp/s/bc7e9e110ea9a2775b96ded61dedf808"></script>
            <!-- admax -->
        </div>

        <div id="content" itemprop="mainContentOfPage" itemscope itemtype="http://schema.org/WebPageElement">""" + ("""
            <section>
                <h2>フィード RSS2.0</h2>
                <ul id="feeds">
                    <li><a href=\"""" + uribase + """">すべて</a></li>
                    <li><a href=\"""" + uribase + """/text">テキスト</a></li>
                    <li><a href=\"""" + uribase + """/photo">画像</a></li>
                    <li><a href=\"""" + uribase + """/quote">引用</a></li>
                    <li><a href=\"""" + uribase + """/link">リンク</a></li>
                    <li><a href=\"""" + uribase + """/chat">チャット</a></li>
                    <li><a href=\"""" + uribase + """/audio">音声</a></li>
                    <li><a href=\"""" + uribase + """/video">動画</a></li>
                    <li><a href=\"""" + uribase + """/answer">質問</a></li>
                </ul>
            </section>

            <section>
                <h2>利用停止</h2>
                <p>
                    TbrFeed から、あなたのアカウントを削除し、フィードの URI を無効にします。
                    Tumblr のアカウントは削除されません。
                    ログインすれば再度利用することができます。
                </p>
                <form action="suspend.cgi" method="POST">
                    <button type="submit">利用停止</button>
                </form>
            </section>""" if loggedin else """
            <div itemscope itemtype="http://schema.org/WebApplication">
                <meta itemprop="name" content="TbrFeed" />
                <meta itemprop="author" content="azyobuzin" />
                <meta itemprop="contributor" content="yut831" />

                <p itemprop="description">TbrFeed は Tumblr のダッシュボードを RSS に変換する Web サービスです。</p>

                <section>
                    <h2>利用方法</h2>
                    <p>
                        ログイン後、次の中から購読したい投稿のタイプを選択して、煮るなり焼くなりしてください。<br>
                        <img src="img/41042c.png" width="497" height="66" alt="スクリーンショット" itemprop="screenshot" />
                    </p>
                </section>

                <section>
                    <h2>注意</h2>
                    <ol>
                        <li itemprop="browserRequirements">Cookie が有効になっていないとログインできません。</li>
                        <li>Tumblr の API の内容をそのまま RSS 2.0 に変換しているだけなので、短時間に大量に取得すると、このサーバーと Tumblr のサーバーに負担がかかります。絶対にやるなよ？絶対だぞ？</li>
                    </ol>
                </section>

                <section>
                    <h2>利用開始</h2>
                    <form action="authorize.cgi" method="GET">
                        <p>
                            認証情報は、 Tumblr API の利用のみに使われます。
                            「このアプリケーションがあなたのTumblrアカウント情報を読み書きすることを許可しますか? 」と表示されますが、読み取りしか行いません。
                        </p>
                        <button type="submit">Sign in with Tumblr</button>
                    </form>
                </section>

                <section>
                    <h2>お問い合わせ</h2>
                    <p>
                        要望・不具合報告は、Twitter <a href="https://twitter.com/intent/tweet?screen_name=azyobuzin" class="twlink">@azyobuzin</a> までお願いします。<br>
                        あと、 <a href="https://twitter.com/intent/tweet?button_hashtag=tbrfeed" class="twlink">#tbrfeed</a> タグをつけてツイートすれば見たり見なかったりします。
                    </p>
                </section>

                <section>
                    <h2>オープンソースプロジェクト</h2>
                    <p>ソースコードを <a href="https://github.com/azyobuzin/TbrFeed">GitHub</a> で公開しています。</p>
                </section>

                <section>
                    <h2>使用ライブラリ</h2>
                    <p>TbrFeed は、 Python を用いて開発されており、以下の外部ライブラリを使用しています。</p>
                    <ul>
                        <li><a href="https://github.com/simplegeo/python-oauth2">python-oauth2</a></li>
                        <li><a href="http://mysql-python.sourceforge.net/">MySQL-Python</a></li>
                        <li><a href="http://labix.org/python-dateutil/">python-dateutil</a></li>
                        <li><a href="https://bitbucket.org/bbangert/webhelpers/overview">WebHelpers</a></li>
                    </ul>
                </section>
            </div>""") + """
        </div>

        <div id="footer" itemscope itemtype="http://schema.org/WPFooter">
            <ul id="share">
                <li style="width:68px"><div class="g-plusone" data-size="medium" data-href="http://tbrfeed.azyobuzi.net/"></div></li>
                <li style="width:105px"><div class="fb-like" data-href="http://tbrfeed.azyobuzi.net/" data-send="false" data-layout="button_count" data-width="450" data-show-faces="true"></div></li>
                <li style="width:100px"><a href="https://twitter.com/share" class="twitter-share-button" data-url="http://tbrfeed.azyobuzi.net/" data-lang="ja" data-related="azyobuzin" data-hashtags="tbrfeed" data-dnt="true">ツイート</a></li>
            </ul>
            <div id="copyright">
                ©<span itemprop="copyrightYear">2012</span>
                <span itemprop="copyrightHolder author" itemscope itemtype="http://schema.org/Person"><a itemprop="name url" href="http://www.azyobuzi.net/">azyobuzin</a></span>,
                Special thanks <span itemprop="contributor" itemscope itemtype="http://schema.org/Person"><a itemprop="name url" href="http://yut.ifdef.jp/">yut831</a></span>
            </div>
        </div>

        <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>
        <script type="text/javascript">
          window.___gcfg = {lang: 'ja'};

          (function() {
            var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
            po.src = 'https://apis.google.com/js/plusone.js';
            var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
          })();
        </script>
    </body>
</html>
"""
