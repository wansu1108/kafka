package client;

public class DeviceTask implements Runnable {

    private final Device device;

    public DeviceTask(Device device) {
        this.device = device;
    }

    @Override
    public void run() {
        try {
            while (device.isOn() && !Thread.currentThread().isInterrupted()) { // 디바이스가 켜져있을때 동작.
                try {
                    double nextIntervalMin = device.nextIntervalMinutes();
                    long sleep = (long) (nextIntervalMin * 60_000);
                    Thread.sleep(sleep);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt(); // 인터럽트 상태 복구
                    break; // 루프 종료
                }
                device.generateValue(); // 센서 값 생성
                send(SendType.DATA);
            }   
        } finally {
            send(SendType.SHUTDOWN);
        }
    }

    public void onDevice() {
        device.setOn(true);
    }

    public void shutdownDevice() {
        device.setOn(false);
    }

    // device정보를 서버에 전달한다.
    private void send(SendType sendType) {
        long ts = System.currentTimeMillis();
        System.out.printf("[%s] ts=%d, type=%s, value=%.3f%n",
                      device.getId(), ts, sendType, device.getValue());

    }
}
