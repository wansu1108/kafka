package client;

import java.util.Random;

public class Device {
    private String id;
    private double lam;
    
    public Device(String id, double lam) {
        this.id = id;
        this.lam = lam;
    }

    public String getId() {
        return id;
    }

    public Double getLam() {
        return lam;
    }

    // 1초 동안 발생하는 이벤트 개수 시뮬레이션
    public int generateEvents(Random random) {
        return DeviceGenerator.samplePoisson(lam, random);
    }

    @Override
    public String toString() {
        return "Device{id='" + id + "', lam=" + lam + "}";
    }
}
