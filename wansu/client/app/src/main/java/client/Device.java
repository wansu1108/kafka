package client;

import java.util.Random;

public class Device {
    private String id;
    private double lam;
    private double value;
    private Random random;
    private boolean on = false;

    public Device(int seq, double lamMean, double lamStd, Random random) {
        this.id = generateId("dev-", seq);
        this.lam = generateLambda(lamMean, lamStd, random);
        this.random = random;
    }

    private double generateLambda(double lamMean, double lamStd, Random random) {
        // 정규분포 난수 생성
        double lam = lamMean + random.nextGaussian() * lamStd;
        // 최소값 보정
        return Math.max(0.1, lam);
    }

    private String generateId(String prefix, int seq) {
        return String.format("%s%04d", prefix, seq);
    }

    // 지수분포 간격 샘플링 (분 단위)
    public double nextIntervalMinutes() {
        double u = random.nextDouble();
        return -Math.log(1 - u) / lam;
    }

    // value 생성 (랜덤 변동)
    public void generateValue() {
        value += random.nextDouble() - 0.5;
        this.value = Math.round(value * 1000.0) / 1000.0;
    }

    public String getId() {
        return id;
    }

    public double getLam() {
        return lam;
    }

    public boolean isOn() {
        return on;
    }

    public void setOn(boolean on) {
        this.on = on;
    }

    public double getValue() {
        return value;
    }

    @Override
    public String toString() {
        return "Device{id='" + id + "', lam=" + lam + ", value=" + value + "}";
    }
}
