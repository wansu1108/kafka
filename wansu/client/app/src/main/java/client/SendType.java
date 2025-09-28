package client;

public enum SendType {
    DATA("DATA", "데이터 전송"),
    SHUTDOWN("SHUTDOWN", "디바이스 셧다운")
    ;

    private SendType(String type, String desc) {
        this.type = type;
        this.desc = desc;
    }

    private String type;
    private String desc;

    public String getType() {
        return type;
    }

    public String getDesc() {
        return desc;
    }
}
