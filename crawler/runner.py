# NOTE: mấy ô cần đảm bảo cài edgedriver.exe rồi và thêm n vào system environment path của máy rồi
# thì mới chạy được nhé. K thì mấy ô f chỉnh link dẫn tới edgedriver.exe ở file threads.py

from threads import *
from databases import *

# Lấy database, mongodb_connection_string t lưu ở file UDPTDLTM/configuration; tên database là udptdltm-database
# Phần này mấy ô k cần thay đổi tham số, để truy cập được vào db của t.
db = get_database(mongodb_connection_string, "udptdltm-database")

# Lấy collection lưu các link, t lưu ở collection store_links.
cl_link = create_collection("store_links", db)

# Lấy dataframe lưu các link:
links = get_all_documents(cl_link)

# Lấy các link trong khoảng mấy ô được phân công, phần này mấy ô tự chỉnh lại lấy cho đúng khoảng nhé
# Vì mỗi ô f làm rất nhiều link. Nên mấy ô có thể tự chia nhỏ phần của mình ra nhiều lần.
# Ví dụ ô f làm 6000 link từ 0 tới 5999. Có thể chia thành 0 tới 1999, rồi chạy 1 lần
# Khi nào rảnh chạy tiếp từ 2000 tới 3999...
# Theo t ước tính thì 2000 link chạy mất gần 2 tiếng nếu mạng mạnh
# Ví dụ lấy link id từ 0 tới 1999: links[0:2000]
my_links = links[23220:25220]

# Tạo/truy cập collection, thông tin cửa hàng t sẽ lưu ở collection store_info.
# Mấy ô muốn test j đó thì đổi tên collection thành tên khác nhé. Để nguyên mà test lỗi là toang
cl = create_collection("store_info", db)

# Hàm bên dưới t khai báo ở threads.py. Tham số 1 là link, tiếp là số threads, cuối là collection để lưu vào
# Quá trình chạy thì t lưu n ở UDPTDLTM/logger.log rồi, mấy ô có thể quan sát bằng file đó.
# Chạy ok thì mấy ô đổi tên thành tên mình hay j đó r chuyển n vào folder logger.
# Nếu lưu trên mongodb bị lỗi, thì n sẽ tự động chuyển sang lưu và UDPTDLTM/data.csv.
# Lúc này mấy ô cần đổi tên file thành tên khác r bỏ n vào folder data.
multi_thread_get_info(my_links['href'], 5, cl)

# Hàm này dùng để chuyển data trong collection thành file csv lưu ở path được truyền vào.
# collection_to_csv(cl, 'data/store_info_updated.csv')
