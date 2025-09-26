package client;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class DeviceGenerator {
    public static Random random = new Random();

    public static List<Device> genDevices(int n, double lamMean, double lamStd) {
        List<Device> devs = new ArrayList<>();

        for(int i=1; i<=n; i++) { 
            // 정규분포 난수 생성
            double lam = lamMean + random.nextGaussian() + lamStd;

            // 최소값 보정
            lam = Math.max(0.1, lam);

            // dev-0000, dev-0001 형식의 ID 생성
            String id = String.format("dev-%04d", i);

            devs.add(new Device(id, lam));
        }

        return devs;
    }

    public static int samplePoisson(double lambda, Random random) {
        double L = Math.exp(-lambda);
        int k = 0;
        double p = 1.0;
    
        do {
            k++;
            p *= random.nextDouble();
        } while (p > L);
    
        return k - 1;
    }

}
