#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import types

import CaboCha
from xml.etree.ElementTree import fromstring


class Token:
    '''形態素クラス
    surface:表層文字列
    id:形態素番号
    features:解析結果を格納する辞書。
        class:品詞
        subclass[123]:品詞細分類1,2,3
        conj:活用形(conjugation)
        form:活用型(conjugation form)
        orig:原形(original form)
        read:読み
        pron:発音(pronounciation)
    ne:固有表現'''

    FEATURE_NAMES = ['class',
                     'subclass1',
                     'subclass2',
                     'subclass3',
                     'conj',
                     'form',
                     'orig',
                     'read',
                     'pron']

    def __init__(self, surface, id, feature, ne):
        self.surface = surface
        self.id = int(id)
        self.features = dict(
            zip(Token.FEATURE_NAMES, feature.split(',') + ['*', '*', '*', '*', '*', '*', '*', '*', '*']))
        self.ne = ne

        self.next = None

    def __str__(self):
        '''printすると表層形が得られる'''
        return self.surface

    def to_string(self):
        '''全ての形態素情報を返す'''
        return '%s\t%s\t%s' % (self.surface, ','.join([self.features[fn] for fn in Token.FEATURE_NAMES]), self.ne)


class Chunk:
    '''文節クラス
    tokens:文節内の形態素(Tokenクラス）のリスト
    id:文節番号
    link:係り先文節番号
    rel:係り種別（'D':依存）
    score:係り関係のスコア
    head:主辞の形態素
    func:機能語の形態素'''

    def __init__(self, tokens, id, link, rel, score, head, func):
        self.tokens = tokens
        self.id = int(id)
        self.link = int(link)
        self.rel = rel
        self.score = float(score)
        self.head_pos = int(head)
        self.func_pos = int(func)
        self.head = str(tokens[self.head_pos]).encode('utf-8')
        self.func = str(tokens[self.func_pos]).encode('utf-8')
        # self.head = tokens[self.head_pos]
        # self.func = tokens[self.func_pos]
        self.parents = None

    def __str__(self):
        '''printすると表層形が得られる'''
        return ''.join([t.__str__() for t in self.tokens])

    def surface(self):
        '''上に同じ'''
        return ''.join([t.__str__() for t in self.tokens])

    def to_string(self):
        '''全ての係り受け情報を返す'''
        ret = '%s %s%s %s/%s %s\n' % (self.id, self.link, self.rel, self.head_pos, self.func_pos, self.score)
        for tok in self.tokens:
            ret += tok.to_string() + '\n'
        return ret


class CaboChaWrapper:
    '''CaboChaのラッパークラス
    まずはparse()を使って解析'''

    def __init__(self, charset):
        '''初期化
        charset:MeCab, CaboChaで使用している文字コード'''

        self.charset = charset
        # self.cabocha = CaboCha.Parser('--charset=%s -u user.dic' % charset)
        self.cabocha = CaboCha.Parser('--charset=%s' % charset)
        # self.cabocha = CaboCha.Parser('--charset=%s -d C:\mecab-ipadic-neologd' % charset)
        # 形態素リスト
        self.tokens = []
        # 文節リスト
        self.chunks = []

    def parse(self, string, out=False):
        '''係り受け解析
        string:文字列
        out:解析結果を文字列として出力するか'''

        # 形態素リストと文節リストを空に
        self.tokens = []
        self.chunks = []

        # 文字コード変換
        str2 = string.encode(self.charset, 'ignore')
        #print(type(string))
        #print(type(str2))
        # 解析
        #tree = self.cabocha.parse(str2)
        tree = self.cabocha.parse(string)
        # 京都大学コーパスフォーマットに基づいた出力
        # if out:
        # print tree.toString(CaboCha.FORMAT_LATTICE).decode(self.charset)

        # XML形式で出力
        xml_str = tree.toString(CaboCha.FORMAT_XML).encode(self.charset)

        # ルート要素
        elem = fromstring(xml_str)

        # 形態素リスト作成
        for te in elem.findall(".//tok"):
            tok = Token(te.text,
                        te.get('id'),
                        te.get('feature'),
                        te.get('ne'))
            self.tokens.append(tok)

        for i in range(len(self.tokens) - 1):
            self.tokens[i].next = self.tokens[i + 1]

        # 文節リスト作成
        for ce in elem.findall(".//chunk"):
            # 文節内の形態素のリスト
            tokens_in_chunk = []
            for te in list(ce):
                for t in self.tokens:
                    if t.id == int(te.get('id')):
                        tokens_in_chunk.append(t)

            # 文節クラス
            ch = Chunk(tokens_in_chunk,
                       ce.get('id'),
                       ce.get('link'),
                       ce.get('rel'),
                       ce.get('score'),
                       int(ce.get('head')) - tokens_in_chunk[0].id,
                       int(ce.get('func')) - tokens_in_chunk[0].id)
            # 文節リストに追加
            self.chunks.append(ch)

    def get_token(self, string):
        '''文字列の属する形態素を得る
        複数該当した場合は最初の一個のみ'''
        t = [t for t in self.tokens if string in t.surface]
        return t[0] if t else None

    def get_chunk(self, token_or_str):
        '''形態素、または文字列の属する文節を得る
        複数該当した場合は最初の一個のみ'''
        if isinstance(token_or_str, Token):
            token = token_or_str
            c = [c for c in self.chunks if token in c.tokens]
            if c:
                return c[0]
            else:
                print('この形態素を含む文節が見つかりません')
                return None
        elif isinstance(token_or_str, str):
            string = token_or_str
            c = [c for c in self.chunks if string in c.surface()]
            if c:
                return c[0]
            else:
                print('この文字列を含む文節が見つかりません')
                return None

    def get_child(self, chunk):
        '''文節の係り先（子）を得る'''
        c = [c for c in self.chunks if c.id == chunk.link]
        if c:
            return c[0]
        else:
            return None

    def get_parents(self, chunk):
        '''文節の係り元（親）のリストを得る'''
        c = [c for c in self.chunks if c.link == chunk.id]
        if c:
            return c
        else:
            return None

    def get_roots(self, chunk):
        '''文節の根（最上の親）のリストを得る'''
        roots = []
        self._get_roots(chunk, roots)
        return roots

    def _get_roots(self, chunk, roots):
        '''文節の根のリストを得る（再帰）'''
        parents = self.get_parents(chunk)
        if parents:
            for p in parents:
                self._get_roots(p, roots)
        else:
            roots.append(chunk)

    def get_path(self, start_chunk, end_chunk):
        '''文節から文節までの経路を得る'''
        path = [start_chunk]
        while True:
            if path[-1] == end_chunk:
                return path
            else:
                if cab.get_child(path[-1]):
                    path.append(cab.get_child(path[-1]))
                else:
                    print('経路が見つかりません')

    def print_out(self):
        '''解析結果をコンソールに出力'''
        for c in self.chunks:
            print
            c.to_string()

    def print_txt(self):
        '''解析結果をテキストファイルに出力'''
        with open("cabocha.txt", "w") as f:
            for c in self.chunks:
                f.write(c.to_string())
                f.write("\n")

    def print_input(self, str, f):
        f.write(u"--------------------\n")
        f.write(u"入力文\n")
        f.write(u"--------------------\n")
        f.write(str)
        f.write("\n")

    def count_word(self, f):
        num_word = 0
        for c in self.chunks:
            num_word += len(c.tokens)

        f.write(u"--------------------\n")
        f.write(u"単語数\n")
        f.write(u"--------------------\n")
        f.write(str(num_word))
        f.write("\n")


if __name__ == "__main__":
    Character_code = 'utf-8'
    print(u"デフォルトの文字コード", sys.getdefaultencoding())
    cab = CaboChaWrapper(Character_code)
    sent = u'私は今自然言語処理の課題をしています'
    # sent = u"「夏が来れば思い出す。はるかな尾瀬遠い空」。唱歌「夏の思い出」でおなじみの尾瀬は山と湿原が美しい景色を織りなす自然の宝庫だ。豊かな高山植物をはじめ、独自の生態系を築いてきた。そんな貴重な環境がニホンジカの侵入や地球温暖化によって損なわれようとしている。実態の把握や保全策の検討に向け、専門家らが来年春、65年ぶりに大規模な調査を実施する。\n 見渡す限り続く広大な湿原。周囲の山にはうっすら紅葉の気配が漂う。東西6キロメートル、南北2キロメートルに及ぶ尾瀬ケ原は国内屈指の山岳湿原だ。9月末に訪れると、雨がちらつくあいにくの天候にもかかわらず、ハイキングを楽しむ多くの人の姿があった。\n 福島、群馬、新潟の3県にまたがる尾瀬は1年の半分が雪に覆われ、春から夏にかけてミズバショウなどの植物が湿原を彩る。国立公園に指定されているため、歩道以外への立ち入りは厳しく制限されており、豊かな自然を維持してきた。ところが近年、異変が生じている。\n その一例が植物の生えていない裸地の存在だ。「ニホンジカが掘り返した跡」と尾瀬国立公園を管理する環境省の牧野友香・自然保護官は説明する。シカはミツガシワと呼ぶ植物を好んで食べる。根や茎をエサにするため、地面が掘り返されたようになるという。尾瀬の象徴ともいえるニッコウキスゲなどもシカに食べられている。\n シカはもともと尾瀬に生息していなかった。侵入が確認されたのは1990年代になってからだ。環境省がシカに発信器を取り付けて行動を調べたところ、奥日光方面と尾瀬の間を移動していることが分かった。シカの数が増え、食料を求めて尾瀬に姿を現すようになった可能性がある。\n 「これまで存在しなかった動植物の影響で尾瀬の生態系が変化している」。横浜国立大学の鈴木邦雄名誉教授は指摘する。観光客の靴に種子がくっついて持ち込まれる外来の植物などもあるという。鈴木名誉教授らは現状把握に向け、2017年度から3年かけて学術調査に乗り出す。\n 尾瀬の学術調査は今回が4回目で、約20年ぶりとなる。尾瀬保護財団(前橋市)が事務局となり、生物や環境保全に詳しい50~60人の専門家が参加する。調査は基礎研究と重点研究の2つの柱があり、鈴木名誉教授は基礎研究部会のリーダーを務める。\n 基礎研究の目的の一つが動植物のリストの作成だ。尾瀬にはシダ以上の高等植物が約900種生息するとされるが、実態はよくわからない。本格的な調査は1950~52年の第1回の学術調査以来、実施してこなかった。自由な立ち入りができなかったことに加え、調査費を確保するのも難しかったからだ。\n 今回の調査では、現地の観察だけでなく、小型無人機ドローンも活用する。上空からの立体映像を使って地形や生物を調べ、シカの影響も探る。「30年後、50年後に検証できるように、現在の尾瀬の姿を記録したい」と鈴木名誉教授は話す。\n もう一つの柱である重点研究では温暖化の影響を調べる。正確な統計はないが、重点研究部会のリーダーである北海道大学の岩熊敏夫名誉教授の推定では、過去100年間で尾瀬の気温は1~2度上がったという。今後も上昇傾向は続くと予想されている。\n 温暖化の影響で、湿原の環境にとって重要な雨や雪が変化する。夏場に日照りが増える一方で、短時間に強い雨が降る傾向が強まっている。1日に200ミリ近い大雨を記録した11年7月には、尾瀬ケ原を囲む至仏山などが崩れ、土砂が湿原に流れ込んだ。\n 冷涼で水の多い尾瀬の湿原では、枯れた植物が分解されずに堆積して泥炭層になっている。湿原の栄養分は少なく、生息できる植物の種類は限られる。それが独自の生態系を築く理由にもなってきた。ところが、山から土砂が流入するとカルシウムやカリウムといった栄養素が湿原に供給され、他の植物が繁殖しやすくなる。\n このため、大雨が頻発するようになると湿原が「富栄養化」し、植生が変わる恐れがある。一方、日照りによって乾燥すれば植物の分解が進みやすくなる。冬場の降雪の減少も湿原に変化を及ぼす可能性がある。岩熊名誉教授は「今世紀末までの温暖化の影響を調べ、打てる手があるなら探りたい」と話す。\n 尾瀬の貴重な生態系をいつまで維持できるのか。「まだ、わからないことばかりだ。だからこそ、今の尾瀬を調査しなければならない」と尾瀬保護財団の坂本充理事は強調する。(生川暁)\n"
    sent = u" iPS細胞が初めて作られてから10年たった。政府はこの間、再生医療の柱と位置づけて研究を推進。iPS細胞から作った目の細胞が初めて患者に移植され、京都大学が臨床に使うiPS細胞の供給を始めるなど、体制は整いつつある。一方で後に続く臨床研究は始まっておらず、実施への課題も浮上している。iPS医療が離陸できるか正念場を迎えている。\n 「CiRA(京都大学iPS細胞研究所)は自分で自分の首を絞めている」。関係者の間で、こんな言葉がささやかれている。独自に作ったiPS細胞の安全基準が厳しすぎ、研究が進めにくくなっているという。\n CiRAは多くの日本人と適合する免疫の型を持つ人から細胞の提供を受け、iPS細胞を作って備蓄。昨年夏から臨床研究を目指す機関に配布を始めた。各機関はこれをもとに臨床に使うiPS細胞を作り、神経や目など目的の細胞に育てて治療に用いる。\n 2014年に実施された最初の臨床研究のように患者から採った細胞でiPS細胞を作っていたのでは、時間もコストも膨らむ。細胞を備蓄し供給すれば、安く迅速に臨床研究が実施できる。日本にiPS医療を普及させる柱となる戦略だ。\n だが提供したiPS細胞の株(同じ細胞の集団)はごく少数だ。ゲノムを徹底的に調べ、がん化などのリスクが極めて小さいものに絞った。\n iPS細胞は、同じ細胞から同じように作っても、株によって目的の細胞への育ちやすさが違う。株が少ないと「思うように研究を進められない」と研究者はこぼす。CiRA所長の山中伸弥京大教授は「過剰な対応だとは思うが、慎重にならざるをえない」と話す。\n だがゲノムに変異があっても、必ずしも実際の危険にはつながらない。極めて低いリスクでも使えないとするなら、臨床研究のハードルは極めて高くなる。\n 何をどこまで調べたらiPS細胞の安全性が担保できるのか。それを明らかにしようと、この9月、製薬業界が動き出した。国立医薬品食品衛生研究所と大日本住友製薬、アステラス製薬、武田薬品工業などが共同でiPS細胞の品質評価法を確立する。ゲノムではなく実際の動物実験や細胞実験を通じて、安全確保に必要な条件を詰める。\n 衛生研の佐藤陽治部長は、日本の方法を「国際標準に提案したい」と力を込める。業界団体と連携し、国際標準につなげる考えだ。\n 研究機関同士の新たな連携も動き出した。臨床研究を目指すCiRAと理研、慶応義塾大学などが共同で、作ったiPS細胞を共通の動物実験で調べる。山中教授は「今までバラバラだった動物実験を集約し、データを共有したい」と話す。\n 安全性の確保は大前提だが、過大なハードルを設けるとコストも時間も跳ね上がり、実用化への足かせになりかねない。必要十分な線をどこに引くのか。その見極めが今後の最大の焦点になる。\n"
    sent = u"スパゲティ・アッラ・アマトリチャーナ発祥の地であるアマトリーチェ市が、8月のイタリア中部地震で大被害を受けた。イタリア料理、特にローマ料理にはなくてはならないアマトリチャーナの名前は世界的に有名、日本でも知っている人は多いと思う。\n アマトリチャーナでは毎年この時期に「スパゲティ・アッラ・アマトリチャーナ祭」が開かれる。今年は50周年で、泊まりがけで来ていた観光客も多く、被害者が増えてしまった。\n イタリア・スローフードのペトリーニ会長は「アマトリチャーナは、貧しくても連帯している農民文化を象徴する料理だ。我々の連帯が一時的な感傷に終わるのではなく、街の再建のために長続きさせたい」として、これから1年、世界中のレストランでアマトリチャーナ1皿につき2ユーロ(220円)をアマトリーチェ市に寄付する運動を提案した。\n グラフィック・デザイナーでブロガーのパオロ・カンパーナ氏は1ユーロを客が、さらに1ユーロを店が赤十字を通して寄付する方法をレストランに呼びかけ、店に張り出すポスターをデザインした。すでに国内外から多くの参加者が名乗り出ている。トリノ市のキアラ・アッペンディーノ市長はこの夏、街の中心のサン・カルロ広場で被災地への募金のためにアマトリチャーナを食べるイベントを開いた。\n 日本にはスパゲティを提供するレストランが数十万軒あるようだが、中世の雰囲気を残したこのすてきな街を再建するため、募金運動に参加する店が多く出てくれればと思う。(茜ケ久保 徹郎)\n"
    sent = "私は学生であるという。"
    sent = "国内発売に当たり「インドのヒット曲集と銘打っても一般の関心は呼ばない。日本人が好きなカレーに引き付けよう」と考えたという。"
    sent = u" 国会で審議入りした環太平洋経済連携協定(TPP)。発効すれば農業、産業分野だけでなく文学の世界にも影響を与える。小説などの著作権の保護期間が従来の50年から70年に延び、昭和の文豪作品の無料公開が先送りされる可能性が高い。著作権切れ作品を無料公開する団体からは「活用されずに死蔵される作品が増えてしまう」と懸念の声が出ている。\n 「長期間にわたって経済的利益を生む作品はごく少数。そのために他の多くの作品を社会で共有できなくなるのは問題だ」。著作権の切れた作品をネット上で無料公開している電子図書館「青空文庫」の運営に携わる翻訳家の大久保ゆうさんはため息をつく。\n三島も川端も\n 現行制度では小説などは原作者の死後50年で著作権が切れ、翌年から原則自由に利用可能。内容を全文入力してネット上で無料公開したり、新たな装丁を施して文庫で販売したりできる。\n 例えば、1965年に死去した谷崎潤一郎や江戸川乱歩は2015年が没後50年に当たり、今年から作品を自由に使えるようになった。青空文庫は今年の1月1日に谷崎の「春琴抄」や乱歩の「二銭銅貨」を公開した。\n ところが、TPP交渉の結果、著作権の保護期間を米国やEUなど海外の主要国が採用する「70年」に延長することになった。条約が発効すれば、これから死後50年を迎える作家の作品は保護期間が20年上積みされ、自由に使えない。\n 没年が67年の山本周五郎や69年の伊藤整、70年の三島由紀夫、71年の志賀直哉、72年の川端康成など、数年内に著作権が切れるはずだった作家の作品の無料利用は先延ばしになる見通しだ。\n欧米は既に70年\n 青空文庫の大久保さんは、著作権切れ作品について「無料で読めるだけでなく、朗読CDを出したり、新しいコンテンツサービスに活用したりできる」と意義を強調。保護期間延長は「世界の文化に大きな害を与える」と訴える。\n 国会図書館は古い所蔵資料をデジタル化してネットで無料公開する事業を進めている。担当者は「50年を過ぎてネット公開できたものが、館内での閲覧しかできなくなるといった影響が出そうだ」と話す。\n 著作権の保護期間は90年代に欧米の多くの国が70年に延ばした。ただ、日本では「著作権者(遺族を含む)の利益を守るため保護期間を延長すべきだ」「過去の作品を広く社会が活用するためには延長すべきでない」などと主張が対立。文化庁の審議会で議論が繰り返されたが、結論を出せない状態が続いていた。\n TPPは米議会の反対などで早期発効に黄信号がともっているが、発効すればその時点から保護期間は延長される。著作権切れ作品の公開に取り組んできた大阪大の岡島昭浩教授(国語学)は「保護期間が長いと没年を調べにくくなり、作品の利用にも支障が生じやすい。『外圧』のような形で70年に延長されてしまうとすれば残念だ」と話している。\n"
    sent = " 私は大学生です。\\n"
    sent = "\n"
    sent = u"スパゲティ・アッラ・アマトリチャーナ発祥の地であるアマトリーチェ市が、8月のイタリア中部地震で大被害を受けた。"
    sent = u"イタリア料理、特にローマ料理にはなくてはならないアマトリチャーナの名前は世界的に有名、日本でも知っている人は多いと思う。"
    sent = u"アマトリチャーナでは毎年この時期に「スパゲティ・アッラ・アマトリチャーナ祭」が開かれる。"
    sent = u"今年は50周年で、泊まりがけで来ていた観光客も多く、被害者が増えてしまった。"
    sent = u"イタリア・スローフードのペトリーニ会長は「アマトリチャーナは、貧しくても連帯している農民文化を象徴する料理だ。"
    sent = u"我々の連帯が一時的な感傷に終わるのではなく、街の再建のために長続きさせたい」として、これから1年、世界中のレストランでアマトリチャーナ1皿につき2ユーロ(220円)をアマトリーチェ市に寄付する運動を提案した。"
    sent = u"グラフィック・デザイナーでブロガーのパオロ・カンパーナ氏は1ユーロを客が、さらに1ユーロを店が赤十字を通して寄付する方法をレストランに呼びかけ、店に張り出すポスターをデザインした。"
    sent = u"すでに国内外から多くの参加者が名乗り出ている。"
    sent = u"トリノ市のキアラ・アッペンディーノ市長はこの夏、街の中心のサン・カルロ広場で被災地への募金のためにアマトリチャーナを食べるイベントを開いた。"
    sent = u"日本にはスパゲティを提供するレストランが数十万軒あるようだが、中世の雰囲気を残したこのすてきな街を再建するため、募金運動に参加する店が多く出てくれればと思う。"
    sent = u"そうした魚介が豊富な海辺の集落に伝わってきたのが、おんこ寿司です"
    sent = u"願いをかなえてくれたのが、志摩市の民宿や飲食店の女将らでつくる「志摩いそぶえ会」のメンバーです"
    sent = u"郷土の食文化を継承しようと２００３年に発足"
    sent = u"郷土の食文化を継承しようと2003年に発足"
    sent = u"三重県志摩地方の郷土寿司といえば、新鮮なカツオをしょうゆダレに漬け込んで酢飯に混ぜた「てこね寿司」が有名ですが、もう一つ、地元で長く愛されてきた「おんこ寿司」があります"
    sent = u"９月中旬、和具の隣の集落、越賀にある志摩市観光協会志摩案内所を訪問しますと、エプロン姿の４人の女性が笑顔で出迎えてくれました"
    sent = u"志摩いそぶえ会代表で民宿「べート・シャローム」を営む石原幸子さん（７９）が教えてくれました"
    sent = u"▽...日本では一度採用した社員の解雇が難しいため、大卒採用は雇用の調整弁の一つとして、景気変動を追う形で増加と減少を繰り返してきた。"
    sent = u"†††"
    sent = u"「このまま放置すれば生活保護の高齢者が大幅に増えかねない」(清家篤・慶応義塾長)ともいえる。"
    sent = u" iPS細胞が初めて作られてから10年たった。政府はこの間、再生医療の柱と位置づけて研究を推進。iPS細胞から作った目の細胞が初めて患者に移植され、京都大学が臨床に使うiPS細胞の供給を始めるなど、体制は整いつつある。一方で後に続く臨床研究は始まっておらず、実施への課題も浮上している。iPS医療が離陸できるか正念場を迎えている。\n 「CiRA(京都大学iPS細胞研究所)は自分で自分の首を絞めている」。関係者の間で、こんな言葉がささやかれている。独自に作ったiPS細胞の安全基準が厳しすぎ、研究が進めにくくなっているという。\n CiRAは多くの日本人と適合する免疫の型を持つ人から細胞の提供を受け、iPS細胞を作って備蓄。昨年夏から臨床研究を目指す機関に配布を始めた。各機関はこれをもとに臨床に使うiPS細胞を作り、神経や目など目的の細胞に育てて治療に用いる。\n 2014年に実施された最初の臨床研究のように患者から採った細胞でiPS細胞を作っていたのでは、時間もコストも膨らむ。細胞を備蓄し供給すれば、安く迅速に臨床研究が実施できる。日本にiPS医療を普及させる柱となる戦略だ。\n だが提供したiPS細胞の株(同じ細胞の集団)はごく少数だ。ゲノムを徹底的に調べ、がん化などのリスクが極めて小さいものに絞った。\n iPS細胞は、同じ細胞から同じように作っても、株によって目的の細胞への育ちやすさが違う。株が少ないと「思うように研究を進められない」と研究者はこぼす。CiRA所長の山中伸弥京大教授は「過剰な対応だとは思うが、慎重にならざるをえない」と話す。\n だがゲノムに変異があっても、必ずしも実際の危険にはつながらない。極めて低いリスクでも使えないとするなら、臨床研究のハードルは極めて高くなる。\n 何をどこまで調べたらiPS細胞の安全性が担保できるのか。それを明らかにしようと、この9月、製薬業界が動き出した。国立医薬品食品衛生研究所と大日本住友製薬、アステラス製薬、武田薬品工業などが共同でiPS細胞の品質評価法を確立する。ゲノムではなく実際の動物実験や細胞実験を通じて、安全確保に必要な条件を詰める。\n 衛生研の佐藤陽治部長は、日本の方法を「国際標準に提案したい」と力を込める。業界団体と連携し、国際標準につなげる考えだ。\n 研究機関同士の新たな連携も動き出した。臨床研究を目指すCiRAと理研、慶応義塾大学などが共同で、作ったiPS細胞を共通の動物実験で調べる。山中教授は「今までバラバラだった動物実験を集約し、データを共有したい」と話す。\n 安全性の確保は大前提だが、過大なハードルを設けるとコストも時間も跳ね上がり、実用化への足かせになりかねない。必要十分な線をどこに引くのか。その見極めが今後の最大の焦点になる。\n"
    sent = u"イタリア"
    sent = u"イタリア アメリカ"
    sent = u"尾瀬で・年ぶりの大規模調査　温暖化の影響に重点"
    sent = u"被害者が増えてしまいました"
    # print type(sent)
    cab.parse(sent, True)
    print(u"--------------------CaboCha解析結果--------------------")
    cab.print_out()
    print(u"--------------------変数表示--------------------")
    for i in range(len(cab.chunks)):
        print("------------------------------------------")
        print(len(cab.chunks), "chunks_len")
        # print cab.chunks[i], "cab.chunks[%s]" % i
        print(cab.chunks[i].id, "id")
        print(cab.chunks[i].link, "link")
        print(cab.chunks[i].rel, "rel")
        print(cab.chunks[i].score, "score")
        print(cab.chunks[i].head, "head")
        print(cab.chunks[i].func, "func")
        for j in range(len(cab.chunks[i].tokens)):
            print("---------------------")
            print(len(cab.chunks[i].tokens), "tokens_len")
            print(cab.chunks[i].tokens[j].surface, "surface")
            print(cab.chunks[i].tokens[j].id, "id")
            print(cab.chunks[i].tokens[j].features["form"], "form")
            print(cab.chunks[i].tokens[j].features["pron"], "pron")
            print(cab.chunks[i].tokens[j].features["class"], "class")
            print(cab.chunks[i].tokens[j].features["subclass1"], "subclass1")
            print(cab.chunks[i].tokens[j].features["subclass2"], "subclass2")
            print(cab.chunks[i].tokens[j].features["subclass3"], "subclass3")
            print(cab.chunks[i].tokens[j].features["conj"], "conj")
            print(cab.chunks[i].tokens[j].features["orig"], "orig")
            print(cab.chunks[i].tokens[j].features["read"], "read")
            print(cab.chunks[i].tokens[j].ne, "ne")

    '''文節クラス
    tokens:文節内の形態素(Tokenクラス）のリスト
    id:文節番号
    link:係り先文節番号
    rel:係り種別（'D':依存）
    score:係り関係のスコア
    head:主辞の形態素
    func:機能語の形態素'''

    '''形態素クラス
    surface:表層文字列
    id:形態素番号
    features:解析結果を格納する辞書
        class:品詞
        subclass[123]:品詞細分類1,2,3
        conj:活用形(conjugation)
        form:活用型(conjugation form)
        orig:原形(original form)
        read:読み
        pron:発音(pronounciation)
    ne:固有表現'''

    # 文字列はすべてunicodeで出力しています(文字コードがutf-8のstr型をdecode)
