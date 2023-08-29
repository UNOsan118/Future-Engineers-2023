import cv2 # 予選用 # 本番用
import numpy as np
import time
# import serial


def red_detect(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 赤色のHSVの値域1
    hsv_min = np.array([0, 60, 35])
    hsv_max = np.array([2, 255, 255])
    mask1 = cv2.inRange(hsv, hsv_min, hsv_max)

    # 赤色のHSVの値域2
    hsv_min = np.array([150, 60, 35])
    hsv_max = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, hsv_min, hsv_max)

    mask = mask1 + mask2
    return mask


def green_detect(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 緑色のHSVの値域
    hsv_min = np.array([40, 70, 95])
    hsv_max = np.array([70, 255, 255])

    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    return mask


def orange_detect(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 橙色のHSVの値域
    hsv_min = np.array([0, 100, 100]) # 5, 10, 10
    hsv_max = np.array([17, 250, 255]) # 17, 250, 255

    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    return mask

def blue_detect(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 青色のHSVの値域
    hsv_min = np.array([100, 0, 80]) # 85, 40, 40
    hsv_max = np.array([115, 255, 255]) # 115, 255, 255

    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    return mask


def black_detect(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 黒色のHSVの値域
    hsv_min = np.array([0, 0, 0])
    hsv_max = np.array([180, 255, 50])

    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    return mask


def analysis_blob(binary_img):  # 主に標識をブロブ解析するメソッド
    max_blob = {}

    # connectedComponentsWithStatsはオブジェクト（連結領域）を検出するメソッド
    data = cv2.connectedComponentsWithStats(binary_img)

    # ラベルの数（背景もラベリングされるので、オブジェクトの数はdata[0] - 1となる
    n_labels = data[0] - 1

    # 起動時やオブジェクトが完全にない場合に、背景しか抽出されない場合がある
    if n_labels == 0:
        # 例外の時、max_blobに値を突っ込んでおいた方が都合がいい
        # areaが0なので何も起こらない
        max_blob["upper_left"] = (0, 0)  # 左上座標
        max_blob["width"] = 0
        max_blob["height"] = 0
        max_blob["area"] = 0
        max_blob["center"] = (0, 0)

        return max_blob

    # 背景は0とラベリングされるので、最初の行を削除して格納する
    # statsにはそのラベルの {左上のx座標、左上のy座標、幅、高さ、面積}の情報が格納されている
    stats = np.delete(data[2], 0, axis=0)

    # オブジェクトの重心
    centroids = np.delete(data[3], 0, axis=0)

    # 面積が最大値のラベルのインデックス
    max_area_index = np.argmax(stats[:, 4])

    # 一番大きいオブジェクトの情報を抽出
    # 面積（1280×720のうちのピクセル数、環境によって違うかも）
    max_blob["area"] = stats[:, 4][max_area_index]
    max_blob["center"] = centroids[max_area_index]  # 中心座標

    return max_blob


def analysis_blob_line(binary_img):  # 線をブロブ解析するメソッド
    max_blob = {}

    # connectedComponentsWithStatsはオブジェクト（連結領域）を検出するメソッド
    data = cv2.connectedComponentsWithStats(binary_img)

    # ラベルの数（背景もラベリングされるので、オブジェクトの数はdata[0]-1となる
    n_labels = data[0] - 1

    # 起動時やオブジェクトが完全にない場合に、背景しか抽出されない場合がある
    if n_labels == 0:
        # 例外の時、max_blobに値を突っ込んでおいた方が都合がいい
        # areaが0なので何も起こらない
        max_blob["upper_left"] = (0, 0)  # 左上座標
        max_blob["width"] = 0
        max_blob["height"] = 0
        max_blob["area"] = 0
        max_blob["center"] = (0, 0)
        return max_blob

    # 背景は0とラベリングされるので、最初の行を削除して格納する
    # statsにはそのラベルの {左上のx座標、左上のy座標、幅、高さ、面積}の情報が格納されている
    stats = np.delete(data[2], 0, axis=0)

    # オブジェクトの重心
    centroids = np.delete(data[3], 0, axis=0)

    # 面積が最大値のラベルのインデックス
    max_area_index = np.argmax(stats[:, 4])

    # 横幅が最大値のインデックス
    max_width_index = np.argmax(stats[:, 2])
    height, width = binary_img.shape[:3]

    # 一番大きいオブジェクトの情報を抽出
    max_blob["upper_left"] = (
        stats[:, 0][max_area_index], stats[:, 1][max_area_index])  # 左上座標
    max_blob["width"] = stats[:, 2][max_area_index]  # 幅
    max_blob["height"] = stats[:, 3][max_area_index]  # 高さ
    # 面積（1280×720のうちのピクセル数、環境によって違うかも）
    max_blob["area"] = stats[:, 4][max_area_index]
    max_blob["center"] = centroids[max_area_index]  # 中心座標
    area = stats[:, 4][max_area_index]

    return max_blob


def main():
    # カメラのキャプチャ
    cap = cv2.VideoCapture(0)
    while (cap.isOpened()):
        _, frame = cap.read()
        # frame = cv2.rotate(f, cv2.ROTATE_180)

        # 赤色検出
        mask_red = red_detect(frame)

        # 緑色検出
        mask_green = green_detect(frame)

        # 橙色検出
        mask_orange = orange_detect(frame)

        # 青色検出
        mask_blue = blue_detect(frame)

        # マスク画像をブロブ解析（標識と判定されたブロブ情報を取得）
        max_blob_red = analysis_blob(mask_red)
        max_blob_green = analysis_blob(mask_green)

        # 結果表示
        # cv2.imshow("Frame", frame)
        # cv2.imshow("Mask red", mask_red)
        # cv2.imshow("Mask green", mask_green)
        # cv2.imshow("Mask orange", mask_orange)
        # cv2.imshow("Mask blue", mask_blue)

        # qキーが押されたら途中終了
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def detect_sign_area(cap, mode=""):  # 標識の面積を返すdetect_sign（面積によって動作を変えたいため）
    is_red = False
    is_green = False

    ok_blue = False
    ok_orange = False

    clip_ratio = 0.55 #final 0.475 qualifier 0.6 # clip in the top of image for the specific ratio
    img_shape = (320, 320, 3)
    mask_arr = np.ones(img_shape, dtype=np.uint8)
    mask_arr[:int(clip_ratio*320), :, :] = 0

    assert cap.isOpened(), "カメラを認識していません！"
    _, frame = cap.read()

    cut_frame = cv2.resize(frame, dsize=(320, 320))
    cut_frame = cut_frame * mask_arr
    # cv2.imshow("cut_frame", cut_frame)

    frame = cv2.resize(frame, dsize=(160, 120))

    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    frame = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)

    # 色検出
    mask_red = red_detect(frame)
    mask_green = green_detect(frame)
    mask_orange = orange_detect(frame)
    mask_blue = blue_detect(frame)
    mask_black = black_detect(frame)
    mask_black_left = black_detect(frame)
    mask_black_right = black_detect(frame)
    mask_black_left_middle = black_detect(frame)
    mask_black_right_middle = black_detect(frame)
    mask_black_right_middle = black_detect(frame)
    mask_black_core = black_detect(frame)

    height, width, channels = frame.shape[:3]

    # 色毎のカットする範囲を設定
    mask_red[0:int(4.5 * height/10), :] = 0
    mask_green[0:int(4.5 * height/10), :] = 0
    mask_blue[0:int(3 * height/5), :] = 0
    mask_orange[0:int(3 * height/5), :] = 0

    mask_black_left[0:int(6 * height/10), :] = 0
    mask_black_left[int(6 * height/10):int(height), int(width/2):int(width)] = 0

    mask_black_right[0:int(6 * height/10), :] = 0
    mask_black_right[int(6 * height/10):int(height), 0:int(width/2)] = 0

    mask_black_right_middle[0:int(3 * height/6), :] = 0
    mask_black_right_middle[int(3*height/6):int(5 * height/6), 0:int(width/2)] = 0
    mask_black_right_middle[int(5 * height/6):int(height), ] = 0

    mask_black_left_middle[0:int(3 * height/6), :] = 0
    mask_black_left_middle[int(3 * height/6):int(5 * height/6), int(width/2):int(width)] = 0
    mask_black_left_middle[int(5 * height/6):int(height), :] = 0

    mask_black_core[0:int(3 * height/5), :] = 0
    mask_black_core[int(3 * height/5):int(5 * height/5), 0:int(width/5)] = 0
    mask_black_core[int(3 * height/5):int(5 * height/5), int(4 * width/5):int(width)] = 0

    # ブロブ解析
    blob_red = analysis_blob(mask_red)
    blob_green = analysis_blob(mask_green)
    blob_orange = analysis_blob_line(mask_orange)
    blob_blue = analysis_blob_line(mask_blue)
    blob_black_right = analysis_blob_line(mask_black_right)
    blob_black_left = analysis_blob_line(mask_black_left)
    blob_black_right_middle = analysis_blob_line(mask_black_right_middle)
    blob_black_left_middle = analysis_blob_line(mask_black_left_middle)
    blob_black_core = analysis_blob_line(mask_black_core)

    black_left_area = blob_black_left["area"]
    black_right_area = blob_black_right["area"]
    black_left_middle_area = blob_black_left_middle["area"]
    black_right_middle_area = blob_black_right_middle["area"]
    black_core_area = blob_black_core["area"]

    # どの黒色が画面の何割を占めているかの比
    black_right_ratio = black_right_area * 6 / (width * height)
    black_left_ratio = black_left_area * 6/ (width * height)
    black_left_middle_ratio = black_left_middle_area * 6 / (width * height)
    black_right_middle_ratio = black_right_middle_area * 6 / (width * height)
    black_core_ratio = black_core_area * ((5/2) * (5/3))/(width * height)

    if black_left_ratio < black_left_middle_ratio and black_left_middle_ratio > 0.85 and black_left_ratio > 0.55:
        black_left_ratio = black_left_middle_ratio
    if black_right_ratio < black_right_middle_ratio and black_right_middle_ratio > 0.85 and black_right_ratio > 0.55:
        black_right_ratio = black_right_middle_ratio

    wall_right,wall_left = False,False
    if black_right_ratio > 0.45:
        wall_right = True
    elif black_left_ratio > 0.45:
        wall_left = True
    if not wall_right and not wall_left:
        if black_core_ratio > 0.4:
            black_left_ratio = 0.9
            black_right_ratio = 0.9

    rcx = blob_red["center"][0]
    rcy = blob_red["center"][1]
    gcx = blob_green["center"][0]
    gcy = blob_green["center"][1]


    #赤の物体と緑の物体の大きい方の面積がthreshold以上ならフラグを立てる
    area_red = blob_red["area"]
    area_green = blob_green["area"]

    blue_center_y = 0
    orange_center_y = 0

    # 青線を読んでフラグを立てる条件
    if blob_blue != 0:
        blue_center = blob_blue["center"]
        blue_area = blob_blue["area"]
        if blue_area/(height * width) > 0.004 :
            if blue_center[1] > 7 * height / 10:
                ok_blue = True
            blue_center_y = blue_center[1]/height

    # 橙線を読んでフラグを立てる条件
    if blob_orange != 0:
        orange_center = blob_orange["center"]
        orange_area = blob_orange["area"]
        if orange_area/(width * height) > 0.004 :
            if orange_center[1] > 7 * height / 10:
                ok_orange = True
            orange_center_y = orange_center[1]/height

    orange_center = blob_orange["center"]
    orange_center_x = orange_center[0]/width
    orange_center_y = orange_center[1]/height
    blue_center = blob_blue["center"]
    blue_center_x = blue_center[0]/width
    blue_center_y = blue_center[1]/height

    # 各画像の出力
    # ここから
    # cv2.imshow("Frame", frame)
    # cv2.imshow("Mask red", mask_red)
    # cv2.imshow("Mask green", mask_green)
    # cv2.imshow("Mask orange", mask_orange)
    # cv2.imshow("Mask blue", mask_blue)
    # cv2.imshow("Mask black", mask_black)
    # cv2.imshow("Mask black left", mask_black_left)
    # cv2.imshow("Mask black right", mask_black_right)
    # cv2.imshow("Mask black core", mask_black_core)
    # ここまで

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()

    return frame, cut_frame, mask_red, mask_green, blob_red, blob_green, blue_center_x, orange_center_x, blue_center_y, orange_center_y, ok_blue, ok_orange, black_right_ratio, black_left_ratio

if __name__ == '__main__':
    main()
